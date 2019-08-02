from unittest import TestCase
from helper.config import read_configuration_from_file
from core.bot import Bot
import logging
import os

logger = logging.getLogger()
logger.level = logging.INFO


def clean_profile(results):
    for r in results:
        _, s = r
        s.destroy()


class TestBot(TestCase):

    @classmethod
    def setUpClass(self):
        config = read_configuration_from_file('./test_config.json')
        self.bot = Bot(config)
        self.bot.topics = ['vegan']

    @classmethod
    def tearDownClass(self):
        pass

    def test_get_tweets_per_topic(self):
        tweets = self.bot.get_tweets_per_topic(topic="Twitter")
        self.assertEqual(len(tweets), 100)

    def test_put_like(self):
        send_status, new_status = self.bot.send_status("test")
        self.assertTrue(send_status)
        posted_tweet = self.bot.put_like(new_status)
        self.assertIsNotNone(posted_tweet)
        posted_tweet.destroy()

    def test_put_likes_in_batch(self):
        results = self.bot.put_likes_in_batch(10)
        self.assertTrue(len(results) > 0)
        map(lambda x: self.bot.api.destroy_favorite(x), results)

    def test_put_retweets_in_batch(self):
        results = self.bot.put_retweets_in_batch(10)
        self.assertTrue(len(results) > 0)
        map(lambda x: self.bot.api.destroy_status(x), results)

    def test_post_news_from_rss(self):
        sources = [
            "http://www.repubblica.it/rss/homepage/rss2.0.xml"
        ]
        log_file = "rss_posted.txt"
        if os.path.exists(log_file): os.remove(log_file)
        posted_status = self.bot.post_last_news_from_rss(sources, log_file)
        self.assertIsNotNone(posted_status)
        posted_status.destroy()

    def test_follow_batch(self):
        results = self.bot.follow_batch(5)
        self.assertTrue(len(results) > 0)
        map(lambda x: self.bot.api.destroy_friendship(x[1].screen_name), results)

    def test_unfollow_batch(self):
        results = self.bot.unfollow_batch(5, "popularity")
        self.assertTrue(len(results) > 0)