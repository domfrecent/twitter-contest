
"""Future Improvements:
- Alert for script crash
- One page daily email metric summary
	- Number of retweets, number of follows, size of inbox (messages to respond to) etc.
- Check for existing follow prior to follow
- Generalize for use by other users
	- Instructions for authorization keys
	- Handling for retweet log?
"""

import tweepy
import csv
import time
import json
import secrets


def authorize():
	C_KEY = secrets.C_KEY
	C_SECRET = secrets.C_SECRET
	A_TOKEN = secrets.A_TOKEN
	A_SECRET = secrets.A_SECRET

	auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
	auth.set_access_token(A_TOKEN, A_SECRET)

	api = tweepy.API(auth)
	return api


def addToRtLog(retweet_list, tweet_id):
	retweet_list.append(tweet_id)
	#write to file as well
	f = open('retweet_log.txt', 'a')
	f.write(str(tweet_id))
	f.write("\n")
	f.close()


def getRtLog():
	with open('retweet_log.txt', 'r') as f:
		retweet_list = []

		for line in f:
			retweet_list.append(int(line))
	return retweet_list


def printTweetInfo(data):
	content = data["retweeted_status"]["text"]
	username = data["retweeted_status"]["user"]["screen_name"]
	tweet_id = data["retweeted_status"]["id"]
	print "\n\"" + content + "\"\nuser: " + username + " \nid:" + str(tweet_id) + "\n"


def avoidKeywords():
	return ['makeup', 'palette', 'lipkit', 'eyeshadow', 'lipstick']


def containsBadKey(tweet_contents):
	keyword_flag = False
	for word in avoidKeywords():
		if word in tweet_contents:
			keyword_flag = True

	return keyword_flag


def getTweetTime():
	return last_tweet_time


def getFile():
	return f


"""Primary block below"""
api = authorize()

retweet_list = getRtLog()

last_tweet_time = time.time() - 181 #Initialize last_tweet_time so RT is ready to go


#Process and respond to tweets tracked by stream
class MyStreamListener(tweepy.StreamListener):

	def on_status(self, status):
		#printTweetInfo(status)
		#print status._json

		#Process status data
		json_data = json.dumps(status._json)
		data = json.loads(json_data)


		last_tweet_time = getTweetTime()
		if (time.time() - last_tweet_time) % 10 < 1:
			print time.time() - last_tweet_time

		
		#Make sure time elapsed between previous re-tweet is sufficient (1.5 mins to start)
		if (time.time() - last_tweet_time) < 90:
			pass
			#print "too soon....."

		#Verify that tweet is a retweet, and contains retweeted_status
		elif "retweeted_status" not in data:
			pass
			#print "does not contain retweeted_status, carrying on\n"

		#Verify that bot hasn't previously retweeted the status
		elif data["retweeted_status"]["id"] in retweet_list:
			pass
			#print "I've already retweeted that\n"

		#if all above checks pass then continue with retweet
		else:

			tweet_id = data["retweeted_status"]["id"]
			tweet_contents = data["retweeted_status"]["text"].lower()

			#Keyword filter
			keyword_flag = containsBadKey(tweet_contents)

			printTweetInfo(data)
			api.retweet(tweet_id)

			#check if follow is necessary
			if "follow" in tweet_contents or "flw" in tweet_contents:
				api.create_friendship(data["retweeted_status"]["user"]["id"])

			#reset timer
			global last_tweet_time 
			last_tweet_time = time.time()

			addToRtLog(retweet_list, tweet_id)


	def on_error(self, error_code):
		if error_code == 420:
			print "Yo ass getting rate limited"
			return False

#instantiate MyStreamListener
mystreamListener = MyStreamListener()

stream = tweepy.Stream(auth = api.auth, listener = MyStreamListener())

stream.filter(track=['RT to win'])

