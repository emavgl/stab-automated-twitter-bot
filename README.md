# STAB - Easy to Configure Automated Twitter Bot

**STAB** is a timer based and easy-to-use twitter bot made with Python.

## Disclaimer

I hold no liability for what you do with this bot or what happens to you by using this bot. Abusing this bot can get you banned from Twitter, so make sure to read up on [proper usage](https://help.twitter.com/en/rules-and-policies/twitter-automation) of the Twitter API.

## How to use

0. Visit the portal [https://developer.twitter.com/](https://developer.twitter.com/)
and register a new application

1. Clone the repository

2. Edit the file **config.json** according to the [actions](#actions) you want to perform

```javascript
{
    // Your application credentials
    "consumer_key": "<your_consumer_key>",
    "consumer_secret": "<your_consumer_secret>",
    "access_token": "<your-access-token>",
    "access_token_secret": "<your-access-token-secret>",
    
    // List of target topics
    "topics": ["python", "developer", "javascript"],

    // Define action configurations
    "actions": {
        "likes": {
            "enabled": true,
            "every": 15,
            "target_number": 30,
            "target_tweets": "recent",
            "language": "en"
        },
        "rss": {
            ...
        },
        "follow": {
            ...
        },
        "unfollow": {
            ...
        },
        "retweet": {
            ...
        }
    }
}
```

3. Run the main script

```bash
python3 main.py config.json
```

## Actions

### RSS

`RSS` action posts the latest article from a random source among the one specified in the configuration file

```javascript
    "actions": {
        "rss": {
            "enabled": true,
            "every": 60,
            "log_file": "rss_posted.txt",
            "sources": [
                "feed:http://feeds.feedburner.com/Techcrunch",
                "feed:http://feeds.feedburner.com/TheHackersNews"
            ]
        },
```

- **enabled**: *true* to active the action, *false* otherwise
- **every**: frequency of action dispatch in minutes (e.g. '60' will post every hour) 
- **log_file**: path of log file that will contain an history of posted articles
- **sources**: array of RSS links

### Likes

`Likes` action puts a defined number of likes based on a randomly chosen topic

```javascript
    "actions": {
        "likes": {
            "enabled": true,
            "every": 15,
            "target_number": 30,
            "target_tweets": "recent",
            "language": "en"
        },
```

- **enabled**: *true* to active the action, *false* otherwise
- **every**: frequency of action dispatch in minutes (e.g. '60' will post every hour) 
- **target_number**: number of tweets to like every time the function is dispatched (max 100)
- **target_tweets**:  
    - `recent`: targets the *most recent* tweets about a randomly chosen topic
    - `popular`: targets the *most popular* tweets about a randomly chosen topic
- **language**: to target tweets in a specific language (ISO 639-1 code)

### Follow

`Follow` action follows a defined number of users based on a randomly chosen topic

```javascript
    "actions": {
        "follow": {
            "enabled": true,
            "every": 30,
            "target_number": 10,
            "target_tweets": "recent",
            "language": "en"
        },
```

- **enabled**: *true* to active the action, *false* otherwise
- **every**: frequency of action dispatch in minutes (e.g. '60' will post every hour) 
- **target_number**: number of users to follow every time the function is dispatched
- **target_tweets**:  
    - `recent`: targets the users who posted the *most recent* posts about a randomly chosen topic
    - `popular`: targets the users who posted the *most popular* posts about a randomly chosen topic
- **language**: to target users who posted in a specific language (ISO 639-1 code)

### Unfollow

`Unfollow` action unfollows a defined number of users

```javascript
    "actions": {
        "unfollow": {
            "enabled": true,
            "every": 30,
            "strategy": "popularity",
            "target_number": 5
        },
```

- **enabled**: *true* to active the action, *false* otherwise
- **every**: frequency of action dispatch in minutes (e.g. '60' will post every hour) 
- **target_number**: number of users to un-follow every time the function is dispatched
- **strategy**:  
    - `random`: unfollows random users
    - `popularity`: unfollows the users with a minor number of followers


### Retweet

`Retweet` action retweets a defined number of tweets based on a randomly chosen topic

```javascript
    "actions": {
        "retweet": {
            "enabled": true,
            "every": 45,
            "target_number": 10,
            "target_tweets": "popular",
            "language": "en"
        }
```

- **enabled**: *true* to active the action, *false* otherwise
- **every**: frequency of action dispatch in minutes (e.g. '60' will post every hour) 
- **target_number**: number of posts to retweet every time the function is dispatched
- **target_tweets**:  
    - `recent`: targets the *most recent* posts about a randomly chosen topic
    - `popular`: targets the *most popular* posts about a randomly chosen topic
- **language**: to target posts in a specific language (ISO 639-1 code)

