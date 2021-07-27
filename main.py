import tweepy
import os
from dotenv import load_dotenv


load_dotenv()

banned_words = ["fortnite","call of duty","callofduty","dungeonsanddragons",
"sorare","dnd","oneshotleague","callofcthulhu"]

banned_tags = ["nsfw","dnd","dontretweetosbot"]

oneshot_words = ["niko","alula","calamus","prototype","silver","george","lamplighter","ling","kip",
                "kelvin","magpie","maize","prophet","rue","world machine"]

class Listener(tweepy.StreamListener):
    def on_status(self, status):
        try:

            hashtags = status.entities["hashtags"]
            hashtag_texts = [x["text"].lower() for x in hashtags]

            if hasattr(status, "retweeted_status"):
                raise Exception("already retweeted")

            if status.retweeted:
                raise Exception("is retweeted status")

            if status.in_reply_to_status_id is not None:
                raise Exception("is a comment")

            for banned_tag in banned_tags:
                if banned_tag in hashtag_texts:
                    raise Exception("banned_tags")

                
            for banned_word in banned_words:

                if banned_word in hashtag_texts or banned_word in status.text:

                    contain_oneshot_word = False

                    for oneshot_word in oneshot_words:
                        if oneshot_word in status.text:
                            contain_oneshot_word = True
                            break
                    if not contain_oneshot_word:
                        raise Exception("banned word!")

            blocks = twitter.blocks()
            mutes = twitter.mutes()

            for blocked in blocks:
                if blocked.screen_name == status.user.screen_name:
                    raise Exception("blocked!")

            for mute in mutes:
                if mute.screen_name == status.user.screen_name:
                    raise Exception("muted!")
            
            if hasattr(status, "quoted_status"):
                if "oneshotgame" in hashtag_texts:
                    twitter.create_favorite(status.id)
                    twitter.retweet(status.id)
                raise Exception("is quoted tweet")

            twitter.retweet(status.id)
            twitter.create_favorite(status.id)
        except Exception as e:
            print(e)

auth = tweepy.OAuthHandler(os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"])
auth.set_access_token(os.environ["ACCESS_TOKEN"],os.environ["ACCESS_TOKEN_SECRET"])

twitter = tweepy.API(auth)

listener = Listener()
stream = tweepy.Stream(auth, listener)

while True:
    try:
        print("bot starting...")
        stream.filter(track=["#oneshotgame"])
    except Exception as e:
        print(e)
