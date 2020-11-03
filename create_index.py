import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import *
from utils import hdiv
import jieba
import math


async def run():
    connection = AsyncIOMotorClient(HOST, PORT)
    db = connection["siteInfo"]
    index_ = db["index"]
    await index_.delete_many({})
    content = ""
    async for article in db.rawSiteInfo.find({}, ["content"]):
        content += article.get("content")
    word_list = set(jieba.lcut_for_search(content))
    async for article in db["rawSiteInfo"].find({}, ["url", "content"]):
        content = article.get("content")
        words = jieba.lcut_for_search(content)
        url = article.get("url")
        for word in word_list:
            if word in content:
                document_ = await index_.find_one({"word": word}, ["article_link"])
                if document_ is None:
                    await index_.insert_one({
                        "word": word,
                        "article_link": url + " " + str(hdiv(words.count(word), len(words), len(str(len(words))) + 2))
                    })
                else:
                    value = document_.get("article_link")
                    await index_.find_one_and_update({"word": word}, {
                        "$set": {
                            "article_link": value + "\n" + url + " " + str(hdiv(words.count(word),
                                                                                len(words), len(str(len(words))) + 2))
                        }
                    })
    article_cnt = await db.rawSiteInfo.count_documents({})
    async for record in index_.find({}, ["word", "article_link"]):
        word = record.get("word")
        article_tf = record.get("article_link")
        articles = article_tf.split("\n")
        article_tf_idf = ""
        for article in articles:
            item = article.split()
            tf_idf = float(item[1]) * math.log(float(hdiv(article_cnt, (len(articles) + 1), len(str(articles)) + 2)))
            article_tf_idf += (item[0] + " " + str(tf_idf) + "\n")
        await index_.find_one_and_update({"word": word}, {
            "$set": {
                "article_link": article_tf_idf.rstrip()
            }
        })


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
