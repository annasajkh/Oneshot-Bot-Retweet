import tweepy
import os
import requests
import json
import time
import random
import _thread
import urllib.request
import glob
import requests
import json

from nsfw_detector import predict
from dotenv import load_dotenv
from threading import Thread
from better_profanity import profanity
from profanity_check import predict_prob as predict_profanity

from flask import Flask

app = Flask(__name__)

load_dotenv()

banned_tags = [
    "bilibili", "nsfw", "dnd", "dontretweetosbot", "lewd", "crypto"
    "todayswebtoon"
]

model = predict.load_model("mobilenet_v2_140_224")

class Listener(tweepy.StreamingClient):
    def on_data(self, data):
        try:
            json_data = json.loads(data.decode("utf-8"))
            tweet_data = json_data["data"]

            print(tweet_data["text"])

            if profanity.contains_profanity(tweet_data["text"]):
                raise Exception("profanity!")

            if predict_profanity([tweet_data["text"]])[0] > 0.4:
                raise Exception("profanity!")

            for blocked in blocks:
                if blocked.id == int(tweet_data["author_id"]):
                    raise Exception("blocked!")

            for mute in mutes:
                if mute.id == int(tweet_data["author_id"]):
                    raise Exception("muted!")

            if tweet_data["possibly_sensitive"]:
                raise Exception("nsfw!")

            prediction_result = []

            if "includes" in json_data:
                if "media" in json_data["includes"]:
                    media = json_data["includes"]["media"]
                    for idx, item in enumerate(media):
                        if item["type"] == "photo":
                            urllib.request.urlretrieve(item["url"],
                                                       f"{idx}.jpg")
                            prediction_result.append(
                                (item["url"],
                                 predict.classify(model, f"{idx}.jpg")))

            for url, prediction in prediction_result:
                params = {
                    "url": url,
                    "models": "gore",
                    "api_user": "1024747676",
                    "api_secret": os.environ["GORE_API_KEY"]
                }

                gore_result = json.loads(
                    requests.get('https://api.sightengine.com/1.0/check.json',
                                 params=params).text)
                gore_prob = gore_result["gore"]["prob"]

                print(f"Source: {url}\Gore Prediction: {gore_prob}")

                if gore_prob > 0.4:
                    raise Exception("gore!!!!")

            for url, prediction in prediction_result:
                item = prediction[list(prediction.keys())[0]]

                porn_prediction = item["porn"]
                hentai_prediction = item["hentai"]
                sexy_prediction = item["sexy"]

                print(
                    f"Source: {url}\nPorn Prediction: {porn_prediction}\nHentai Prediction: {hentai_prediction}\nSexy Prediction: {sexy_prediction}"
                )

                if porn_prediction > 0.4 or hentai_prediction > 0.4 or sexy_prediction > 0.4:
                    raise Exception("nsfw!")

            for path in glob.glob("*.jpg"):
                os.remove(path)

            twitter.retweet(tweet_data["id"])
            twitter.create_favorite(tweet_data["id"])

        except Exception as e:
            print(e)

auth = tweepy.OAuthHandler(os.environ["CONSUMER_KEY"],
                           os.environ["CONSUMER_SECRET"])
auth.set_access_token(os.environ["ACCESS_TOKEN"],
                      os.environ["ACCESS_TOKEN_SECRET"])

twitter = tweepy.API(auth)

blocks = twitter.get_blocks()
mutes = twitter.get_mutes()

listener = Listener(os.environ["BEARER_TOKEN"])

@app.route('/')
def main():
    return "The Bot is ALive"

def run():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

keep_alive()

if listener.get_rules().data == None:
    banned_tags_str = " ".join(["-#" + tag for tag in banned_tags])
    removes = '-is:retweet -is:quote -is:reply -url:"https://m.bilibilicomics.com" '

    listener.add_rules(
        tweepy.StreamRule("#oneshotgame " + removes + banned_tags_str))

listener.filter(expansions=["author_id", "attachments.media_keys"],
                tweet_fields=["text", "possibly_sensitive"],
                media_fields=["url", "type"])
