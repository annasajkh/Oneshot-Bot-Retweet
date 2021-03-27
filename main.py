import tweepy
import os

banned = ["fortnite","call of duty","callofduty","dungeonsanddragons","sorare","#dnd","oneshotleague","callofcthulhu"]

class Listener(tweepy.StreamListener):

    def on_status(self, status):
        try:
            if hasattr(status, "retweeted_status"):
                return
            if status.retweeted:
                return
            if status.is_quote_status:
                return
            if status.in_reply_to_status_id is not None:
                return

            for word in banned:
                if word in status.text.lower():
                    return

            blocks = twitter.blocks()
            mutes = twitter.mutes()

            for blocked in blocks:
                if blocked.screen_name == status.user.screen_name:
                    return
            for mute in mutes:
                if mute.screen_name == status.user.screen_name:
                    return
            twitter.retweet(status.id)
            twitter.create_favorite(status.id)
        except:
            print("can't retweet")

auth = tweepy.OAuthHandler(os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"])
auth.set_access_token(os.environ["ACCESS_TOKEN"],os.environ["ACCESS_TOKEN_SECRET"])

twitter = tweepy.API(auth)

listener = Listener()
stream = tweepy.Stream(auth, listener)
stream.filter(track=["#oneshotgame"])