import tweepy
import secretConstants
import cgi
import time
import datetime
from getAlcohol import getAlcoholByName, get_random_alcohol_info_for_tweet
from lastReplied import getLastReplied, setLastReplied

auth = tweepy.OAuthHandler(secretConstants.CONSUMER_KEY, secretConstants.CONSUMER_SECRET)
auth.set_access_token(secretConstants.ACCESS_TOKEN, secretConstants.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

FRANCE_TIME_DIFFERENCE = 60 #my server is in France which messes up the timings
MINUTES_BETWEEN_RANDOM_TWEETS = 20 + FRANCE_TIME_DIFFERENCE
MESSAGE_BUFFER_SECONDS = 2
TWITTER_HANDLE = '@veganAlcoholChe'

def strip_message(message):
    message = message.replace(TWITTER_HANDLE, "")
    message = message.replace(" Hi ", "")
    message = message.replace(" Hi, ", "")
    message = message.replace(" hi ", "")
    message = message.replace(" hi, ", "")
    message = message.replace(" HI ", "")
    message = message.replace(" HI, ", "")
    message = message.replace(" is ", "")
    message = message.replace(" Is ", "")
    message = message.replace("?", "")
    message = message.strip()
    return message

def formatReply(result):
    print (result)
    if result[2] == '':
        reply = result[0] + " is " + result[1] + "."
    elif result[0][2] != '' and result[2]:
        reply = result[0] + " brewed in " + result[2] + " is " + result[1] + "." 
    return reply

def getDMs():
    lastRepliedDmId = getLastReplied(secretConstants.DM_FLAG)
    #reverse so the oldest messages answered first
    dms = api.direct_messages(full_text=True, since_id=lastRepliedDmId)
    dms.reverse()
    return dms

def replyToUnansweredDMs(dms):
    for dm in dms:
        print(dm.sender_screen_name + " sent " + dm.text)
        results = getAlcoholByName(dm.text)
        if len(results) > 10:
            replyToDm = "Sorry but I know a lot of alcohol with that in the name, could you be more specific?"
            api.send_direct_message(screen_name=dm.sender_screen_name, text=replyToDm)
        elif results == []:
            replyToDm = "Unfortunately I cannot find the name of the alcohol you specified in my database, apologies."
            api.send_direct_message(screen_name=dm.sender_screen_name, text=replyToDm)
        else:
            for result in results:
                time.sleep(MESSAGE_BUFFER_SECONDS)
                replyToDm = formatReply(result)
                api.send_direct_message(screen_name=dm.sender_screen_name, text=replyToDm)
        setLastReplied(secretConstants.DM_FLAG, dm.id_str)

def get_mentions():
    last_replied_mention_id = getLastReplied(secretConstants.MENTION_FLAG)
    mentions = api.mentions_timeline(since_id=last_replied_mention_id)
    mentions.reverse()
    return mentions

def reply_to_unanswered_mentions(mentions):
    for mention in mentions:
        print(mention.text)
        message = strip_message(mention.text)
        results = getAlcoholByName(message)
        reply_to_mention = "@" + mention.user.screen_name + " "
        if len(results) > 10:
            reply_to_mention += "Sorry but I know a lot of alcohol with that in the name, could you be more specific?"
            api.update_status(reply_to_mention, in_reply_to_status_id = mention.id_str)
        elif results == []:
            reply_to_mention += "Unfortunately I cannot find the name of the alcohol you specified in my database, apologies."
            api.update_status(reply_to_mention, in_reply_to_status_id = mention.id_str)
        else:
            for result in results:
                time.sleep(MESSAGE_BUFFER_SECONDS)
                reply_to_mention += formatReply(result)
                api.update_status(reply_to_mention, in_reply_to_status_id = mention.id_str)
        setLastReplied(secretConstants.MENTION_FLAG, mention.id_str)

def tweet_about_random_alcohol():
    last_tweet = api.user_timeline(id = api.me().id, count = 1)[0]
    last_tweet_time = datetime.datetime.time(last_tweet.created_at)
    last_tweet_date = datetime.datetime.date(last_tweet.created_at)
    last_tweet_datetime = datetime.datetime.combine(last_tweet_date, last_tweet_time)
    current_time = datetime.datetime.now()
    print(current_time > (last_tweet_datetime + datetime.timedelta(minutes=MINUTES_BETWEEN_RANDOM_TWEETS)))
    if current_time > (last_tweet_datetime + datetime.timedelta(minutes=MINUTES_BETWEEN_RANDOM_TWEETS)):
        tweet = formatReply(get_random_alcohol_info_for_tweet())
        api.update_status(status=tweet)
        print("tweeted: '" + tweet + "'")


def main():
    dms = getDMs()
    replyToUnansweredDMs(dms)
    #Fair few alcohol names over 140 characters
    #mentions = get_mentions()
    #reply_to_unanswered_mentions(mentions)
    tweet_about_random_alcohol()



main()


def tweetAboutAlcohol(alcoholName):
    results = getAlcoholByName(alcoholName)

    tweetQueue = []
    for result in results: 
        status = formatReply(result)
        tweetQueue.append(status)

    for tweet in tweetQueue:
        api.update_status(status=tweet)
        print("tweeted: '" + tweet + "'")

