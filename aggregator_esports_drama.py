from rss import Fetcher
from typing import Dict, List, Tuple

class Aggregator:
    def __init__(self):
        self.name = "ESports Drama"

    def get_name(self) -> str:
        return self.name
    
    def get_min_source_count(self) -> int:
        return 2
    
    def get_cluster_distance_threshold(self) -> int:
        return 0.59
    
    def get_articles(self) -> List[Dict]:
        
        xpaths = [
        {
            '__fetch_url':'https://www.dexerto.com/feed/',
            '__source_name':'Dexerto',
            '__categories':['entertainment'],
            'item': './/item',
            'title': 'title',
            'description': 'description',
            'link': 'link',
            'pub_date': 'pubDate',
            'category': 'category'
        },
        {
            '__fetch_url':'https://gamerant.com/feed/',
            '__source_name':'Game Rant',
            '__categories':['games'],
            'item': './/item',
            'title': 'title',
            'description': 'description',
            'link': 'link',
            'pub_date': 'pubDate',
            'category': 'category'
        },
        {
            '__fetch_url':'https://kotaku.com/rss',
            '__source_name':'Kotaku',
            'item': './/item',
            'title': 'title',
            'description': 'description',
            'link': 'link',
            'pub_date': 'pubDate',
            'category': 'category'
        },
        {
            '__fetch_url':'https://www.gamerevolution.com/feed',
            '__source_name':'Game Revolution',
            '__categories':['news','drama'],
            'item': './/item',
            'title': 'title',
            'description': 'description',
            'link': 'link',
            'pub_date': 'pubDate',
            'category': 'category'
        },
    ]

        articles = []
        for xpath in xpaths:
            articles += Fetcher(max_num_articles=30).fetch(xpath)

        return articles