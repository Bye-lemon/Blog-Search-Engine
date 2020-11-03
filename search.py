import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import *
from utils import *
import operator
import jieba

connection = AsyncIOMotorClient(HOST, PORT)
db = connection["siteInfo"]
index_ = db["index"]


async def query(input_):
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
    if len(sorted_doc) == 0:
        return dict({}), dict({})
    rank_by_score = dict({})
    for url, score in sorted_doc:
        documents_ = await db.rawSiteInfo.find_one({"url": url}, ["title", "update_time", "url", "content", "keywords"])
        keywords = documents_.get("keywords")
        content = documents_.get("content")
        roi = list(set(keywords.split(",")) & set(input_words))
        partial_ = ""
        for roi_ in roi:
            if (ptr := content.find(roi_)) == -1:
                continue
            start_ = max(0, ptr - 20)
            end_ = min(len(content), start_ + 100)
            partial_ = content[start_: end_].replace("\n", "").replace(roi_,
                                                                       "<font style='color:red;'>" + roi_ + "</font>")
            break
        rank_by_score.update({
            documents_.get('title'): {
                "url": documents_.get('url'),
                "update_time": documents_.get('update_time'),
                "score": score,
                "roi": ",".join(roi),
                "highlight": partial_
            }
        })
    rank_by_time = {k: v for k, v in
                    reversed(sorted(rank_by_score.items(), key=lambda x: timeParse(x[1]["update_time"])))}
    return rank_by_score, rank_by_time
