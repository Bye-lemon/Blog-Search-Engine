import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import *
import operator
import jieba
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def run(input_: str):
    connection = AsyncIOMotorClient(HOST, PORT)
    db = connection["siteInfo"]
    index_ = db["index"]
    print(input_)
    input_words = jieba.lcut_for_search(input_)
    rank = dict({})
    for word in input_words:
        documents_ = await index_.find_one({"word": word}, ["word", "article_link"])
        if documents_ is None:
            continue
        links = documents_.get("article_link")
        articles = links.split("\n")
        for article in articles:
            item = article.split()
            url = item[0]
            tf_idf = float(item[1])
            if url in rank:
                rank[url] += tf_idf
            else:
                rank[url] = tf_idf
    sorted_doc = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)
    response = dict({})
    for url, score in sorted_doc:
        documents_ = await db.rawSiteInfo.find_one({"url": url}, ["title", "update_time", "url", "keywords"])
        keywords = documents_.get("keywords")
        roi = list(set(keywords.split(",")) & set(input_words))
        response.update({
            documents_.get('title'): {
                "url": documents_.get('url'),
                "update_time": documents_.get('update_time'),
                "score": score,
                "roi": ",".join(roi)
            }
        })
    return response
