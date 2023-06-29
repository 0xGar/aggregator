import requests
import xml.etree.ElementTree as ET
from dateutil.parser import parse
from typing import List

class Fetcher:
    def __init__(self,max_num_articles:int=20):
        self.max_num_articles = max_num_articles

    def fetch(self,xpaths):
        max_articles = 20
        response = ""
        
        try:
            response = requests.get(xpaths["__fetch_url"])
        except Exception as e:
            print("An error occured:", e)
            print("Problematic xpaths:",xpaths["__fetch_url"])
            print("Continuing...")
            return []
        
        rss_data = response.content
        root = ET.fromstring(rss_data)
        items = []

        include_categories_lowercase = []
        
        if '__categories' in xpaths:
            include_categories_lowercase = [string.lower() for string in xpaths["__categories"]]

        for item in root.findall(xpaths['item']):
            title = item.find(xpaths['title'])
            description = item.find(xpaths['description'])
            link = item.find(xpaths['link'])
            pub_date = item.find(xpaths['pub_date'])

            categories = []
            cats = item.findall(xpaths['category'])
            for category in cats:
                categories.append(category.text)

            # Only include item if item has a category specified within include_categories
            if len(include_categories_lowercase) > 0:
                categories = [string.lower() for string in categories]
                if len(categories) == 0:
                    continue
                if not set(include_categories_lowercase).intersection(categories):
                    continue

            if title == None or title.text == None:
                title = ""
            else: 
                title = title.text
            if description == None or description.text == None:
                description = ""
            else: 
                description = description.text
            if link == None or link.text == None: 
                link = ""
            else:
                link = link.text
            if pub_date == None or pub_date.text == None:
                pub_date = ""
            else:
                pub_date = pub_date.text

            if title == "" or link == "" or pub_date == "":
                continue

            if description == "":
                description = title

            # Convert date to UNIX timestamp if available
            if pub_date:
                pub_date_dt = parse(pub_date)
                pub_date_unix = int(pub_date_dt.timestamp())
            else:
                pub_date_unix = None

            items.append({
                'title': title,
                'description': description,
                'link': link,
                'pub_date': pub_date_unix,
                'source':xpaths["__source_name"]
            })

        return items[:self.max_num_articles]