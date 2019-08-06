from typing import Optional, Tuple, List

import schedule
import time
import tweepy
import random
import logging
import feedparser
import copy
import html

from helper.decorators import quicky_nap
from helper.logs import read_file, write_line_on_file

logger = logging.getLogger("Bot")

class Bot(object):

    def __init__(self, config):
        self.config = config
        self.api = self.setup_api()
        self.topics: List[str] = self.config['topics']
        self.actions: dict = self.config['actions']
        logger.info("Bot has been created")

    def setup_api(self):
        consumer_key = self.config['consumer_key']
        consumer_secret = self.config['consumer_secret']
        access_token = self.config['access_token']
        access_token_secret = self.config['access_token_secret']
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        return api

    def setup_configuration(self):
        """
        Set up the schedule configuration
        """
        if self.actions['follow']['enabled']:
            follow_config = self.actions['follow']
            target_number = follow_config['target_number']
            target_tweets = follow_config['target_tweets']
            language = follow_config['language']
            minutes = follow_config['every']
            schedule.every(minutes).minutes.do(self.follow_batch, target_number, target_tweets, language)
        if self.actions['rss']['enabled']:
            rss_config = self.actions['rss']
            sources = rss_config['sources']
            log_path = rss_config['log_file']
            schedule.every(self.actions['rss']['every']).minutes.do(self.post_last_news_from_rss, sources, log_path)
        if self.actions['likes']['enabled']:
            like_config = self.actions['likes']
            target_number = like_config['target_number']
            target_tweets = like_config['target_tweets']
            language = like_config['language']
            minutes = like_config['every']
            schedule.every(minutes).minutes.do(self.put_likes_in_batch, target_number, target_tweets, language)
        if self.actions['retweet']['enabled']:
            retweet_config = self.actions['retweet']
            target_number = retweet_config['target_number']
            target_tweets = retweet_config['target_tweets']
            language = retweet_config['language']
            minutes = retweet_config['every']
            schedule.every(minutes).minutes.do(self.put_retweets_in_batch, target_number, target_tweets, language)
        if self.actions['unfollow']['enabled']:
            unfollow_config = self.actions['unfollow']
            target_number = unfollow_config['target_number']
            strategy = unfollow_config['strategy']
            minutes = unfollow_config['every']
            schedule.every(minutes).minutes.do(self.unfollow_batch, target_number, strategy)

    def run(self):
        """
        Loops waiting for scheduling a new action
        """
        self.setup_configuration()
        while True:
            schedule.run_pending()
            time.sleep(60)

    def get_tweets_per_topic(self, topic: Optional[str] = None, result_type: str = 'mixed', lang: str = None, count: int = 100) -> List[any]:
        """
        Return a list with 100 tweets matching some search criteria
        :param topic: optional topic, if not specified, it will pick a random topic
        :param result_type: type of search query, gets the 'mixed' tweets by default
        :param lang: language of the tweets (e.g. it for italian)
        :param count: maximum number of tweets to retrieve (maximum 100)
        :return: list of tweets matching the criteria
        """
        if not topic:
            topic = random.choice(self.topics)
        try:
            search_results = list(self.api.search(topic, count=count, result_type=result_type, lang=lang))
            random.shuffle(search_results)
            return search_results
        except Exception as e:
            logger.error("unable to retrieve tweets")
            logger.error(e)
            return []

    def put_likes_in_batch(self, target_number=50, result_type='recent', lang=None) -> List[tweepy.models.Status]:
        """
        Likes in batch a group of tweets given a random topic
        :param lang: tweet language (e.g. it)
        :param target_number: number of tweets to like (maximum 100)
        :param result_type: type of search query, gets the 'recent' tweets by default
        :return: list of successful liked posts
        """
        tweets = self.get_tweets_per_topic(count=target_number, result_type=result_type, lang=lang)
        results = list(map(self.put_like, tweets))
        liked = [x for x in results if x is not None]
        logger.info("Liked: " + str(len(liked)))
        return liked

    def put_retweets_in_batch(self, target_number=50, result_type='recent', lang=None) -> List[tweepy.models.Status]:
        """
        Retweets in batch a group of tweets given a random topic
        :param lang: tweet language (e.g. it)
        :param target_number: number of tweets to retweet (maximum 100)
        :param result_type: type of search query, gets the 'recent' tweets by default
        :return: list of successful retweeted posts
        """
        tweets = self.get_tweets_per_topic(count=target_number, result_type=result_type, lang=lang)
        results = list(map(self.put_retweet, tweets))
        retweeted = [x for x in results if x is not None]
        logger.info("Retweeted: " + str(len(retweeted)))
        return retweeted

    def follow_batch(self, target_number=50, result_type='recent', lang=None) -> List[tweepy.models.User]:
        """
        Follow in batch a group of users given a random topic
        :param lang: tweet language (e.g. it)
        :param target_number: number of users to follow (maximum 100)
        :param result_type: type of search query, gets the 'recent' tweets by default
        :return: list of followed users
        """
        tweets = self.get_tweets_per_topic(count=target_number, result_type=result_type, lang=lang)
        results = list(map(self.follow, tweets))
        followed_users = [x for x in results if x is not None]
        logger.info("Followed: " + str(len(followed_users)))
        return followed_users

    def unfollow_batch(self, target_number: int = 50, strategy: str = "random") -> List[tweepy.models.User]:
        """
        Unfollow target_number of users based on a strategy
        :param target_number: number of users to follow (maximum 200)
        :param strategy: the strategy to use ('random' or 'popularity', 'latest')
        :return: list of unfollowed users
        """
        target_number = min(target_number, 200)
        followers = list(tweepy.Cursor(self.api.friends).items(target_number))
        if strategy == "popularity":
            followers.sort(key=lambda user: user.followers_count)
        elif strategy == "random":
            random.shuffle(followers)
        target_users = followers[:target_number]
        results = list(map(self.unfollow, target_users))
        unfollowed_users = [x for x in results if x is not None]
        log_msg = "Unfollowed: {} using strategy {}".format(len(unfollowed_users), strategy)
        logger.info(log_msg)
        return unfollowed_users

    @quicky_nap
    def post_last_news_from_rss(self, sources: List[str], log_file_path: str) -> Optional[tweepy.models.Status]:
        """
        Send a single post, including the summary and the link of a random
        news among the latest from the configured RSS feeds
        @:param sources: list of RSS sources
        @:param log_file_path: file path for logs
        @:return posted status
        """
        sources = copy.deepcopy(sources)
        random.shuffle(sources)
        posted_articles = read_file(log_file_path)
        for rss_source in sources:
            rss_entries = feedparser.parse(rss_source).entries
            articles_with_summary = [e for e in rss_entries if e.summary]
            latest = articles_with_summary[0]
            post_link = latest.link if 'feedburner_origlink' not in latest else latest['feedburner_origlink']
            if post_link not in posted_articles:
                post_text = latest.title + ". Read more: " + post_link
                posted_tweet = self.send_status(post_text)
                if posted_tweet is not None:
                    logger.info("Posted: " + post_link)
                    write_line_on_file(log_file_path, latest.link)
                    return posted_tweet
        return None

    @quicky_nap
    def send_status(self, text, img=None, reply_to=None) -> Optional[tweepy.models.Status]:
        """
        Sends a new status
        :param text: text to include in the status
        :param img: optional path of an image to include
        :param reply_to: optional reference to a tweet you want to reply
        :return: new status or None if error
        """
        try:
            if img:
                return self.api.update_with_media(img, text, in_reply_to_status_id=reply_to)
            return self.api.update_status(text, in_reply_to_status_id=reply_to)
        except (tweepy.error.RateLimitError, tweepy.error.TweepError) as error:
            error_msg = "Unable to post"
            logger.warning(error_msg)
            return None

    @quicky_nap
    def put_like(self, status: tweepy.models.Status) -> Optional[tweepy.models.Status]:
        """
        Likes the status
        :param status: target status
        :return: liked status or Null if error
        """
        try:
            return status.favorite()
        except (tweepy.error.RateLimitError, tweepy.error.TweepError) as error:
            error_msg = "Unable to put like on tweet {}: {}".format(str(status.id), error.response.text)
            logger.warning(error_msg)
            return None

    @quicky_nap
    def put_retweet(self, status: tweepy.models.Status) -> Optional[tweepy.models.Status]:
        """
        Retweet the status
        :param status: target status
        :return: retweeted status or Null if error
        """
        try:
            return status.retweet()
        except (tweepy.error.RateLimitError, tweepy.error.TweepError) as error:
            error_msg = "Unable to retweet the tweet {}: {}".format(str(status.id), error.response.text)
            logger.warning(error_msg)
            return None

    @quicky_nap
    def follow(self, status: tweepy.models.Status) -> Optional[tweepy.models.Status]:
        """
        Follows the user who post the status
        :param status: target status
        :return: followed user or Null if error
        """
        try:
            return  self.api.create_friendship(status.author.screen_name)
        except (tweepy.error.RateLimitError, tweepy.error.TweepError) as error:
            error_msg = "Unable to follow user {}: {}".format(status.author.screen_name, error.response.text)
            logger.warning(error_msg)
            return None

    @quicky_nap
    def unfollow(self, user: tweepy.models.User) -> Optional[tweepy.models.User]:
        """
        Follows the user who post the status
        :param user: target user
        :return: unfollowed user or Null if error
        """
        try:
            return self.api.destroy_friendship(user.id)
        except (tweepy.error.RateLimitError, tweepy.error.TweepError) as error:
            error_msg = "Unable to follow user {}: {}".format(user.screen_name, error.response.text)
            logger.warning(error_msg)
            return None
