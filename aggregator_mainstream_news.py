from rss import Fetcher 
from typing import Dict, List, Tuple

class Aggregator:
    def __init__(self):
        self.name = "Mainstream News"

    def get_name(self) -> str:
        return self.name
    
    def get_min_source_count(self) -> int:
        return 3
    
    def get_cluster_distance_threshold(self) -> int:
        return 0.5
    
    def get_articles(self) -> List[Dict]:

        xpaths = [
            ### Left-leaning ###
            {
                '__fetch_url':'http://rss.cnn.com/rss/cnn_topstories.rss',
                '__source_name':'CNN',
                'item': './/item',
                'title': 'title',
                'description': 'description',
                'link': 'link',
                'pub_date': 'pubDate',
                'category':'category',
            },
            {
                '__fetch_url':'https://feeds.nbcnews.com/msnbc/public/news',
                '__source_name':'NBC News',
                'item': './/item',
                'title': 'title',
                'description': 'description',
                'link': 'guid',
                'pub_date': 'pubDate',
                'category':'category',
            },
            {
                '__fetch_url':'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
                '__source_name':'New York Times',
                'item': './/item',
                'title': 'title',
                'description': 'description',
                'link': 'link',
                'pub_date': 'pubDate',
                'category':'category',
            },
            ### Right-leaning ###
            {
                '__fetch_url':'https://moxie.foxnews.com/google-publisher/latest.xml',
                '__source_name':'Fox News',
                'item': './/item',
                'title': 'title',
                'description': 'description',
                'link': 'guid',
                'pub_date': 'pubDate',
                'category':'category',
            },
            {
                '__fetch_url':'http://feeds.feedburner.com/dailycaller',
                '__source_name':'Daily Caller',
                'item': './/item',
                'title': 'title',
                'description': 'description',
                'link': 'link',
                'pub_date': 'pubDate',
                'category':'category',
            },
            {
                '__fetch_url':'https://www.washingtontimes.com/rss/headlines/news/',
                '__source_name':'Washington Times',
                'item': './/item',
                'title': 'title',
                'description': 'description',
                'link': 'link',
                'pub_date': 'pubDate',
                'category':'category',
            },
        ]
        
        articles = []
        for xpath in xpaths:
            articles += Fetcher(max_num_articles=30).fetch(xpath)

        return articles