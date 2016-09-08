import tweepy
import secretConstants
from getAlcohol import getAlcoholByName
from lastReplied import getLastReplied, setLastReplied

auth = tweepy.OAuthHandler(secretConstants.CONSUMER_KEY, secretConstants.CONSUMER_SECRET)
auth.set_access_token(secretConstants.ACCESS_TOKEN, secretConstants.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#alcoholName = "GUINESS"
#tweetAboutAlcohol(alcoholName)
#functions need to be declared above calling them it seems...

def formatReply(result):
    if result is None:
            reply = "Sorry, we cannot find the name of the alcohol your specified in our database"
    else: 
        if result[2] == '':
            reply = result[0] + " is " + result[1] + "."
        elif result[0][2] != '' and result[2]:
            reply = result[0] + " brewed in " + result[2] + " is " + result[1] + "." 
    return reply

def getDMs():
    lastRepliedDmId = getLastReplied('DM')
    dms = api.direct_messages(full_text=True, since_id=lastRepliedDmId)
    for dm in dms:
        results = getAlcoholByName(dm.text)
        if len(results) > 12:
            replyToDm = "Sorry, I know a lot of alcohol with that in the name, could you be more specific?"
            api.send_direct_message(screen_name=dm.sender_screen_name, text=replyToDm)
        else:
            for result in results:
                replyToDm = formatReply(result)
                api.send_direct_message(screen_name=dm.sender_screen_name, text=replyToDm)

        print(dm.sender_screen_name + " sent " + dm.text)
        setLastReplied('DM', dm.id_str)

getDMs()


def tweetAboutAlcohol(alcoholName):
    results = getAlcoholByName(alcoholName)

    tweetQueue = []
    for result in results: 
        status = formatReply(result)
        tweetQueue.append(status)

    for tweet in tweetQueue:
        api.update_status(status=tweet)
        print("tweeted: '" + tweet + "'")

