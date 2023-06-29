from aggregator_mainstream_news import Aggregator as NewsAggregator
from aggregator_esports_drama import Aggregator as ESportsDramaAggregator
from article_processor import ArticleProcessor
import json
import time
import os
class Master:
    def __init__(self, aggregators,processor):
        self.aggregators = aggregators
        self.processor = processor
        self.links_file = "links.txt"
        self.link_limit = int(time.time()) - 24 * 60 * 60 #24 hours
        self.buffer = []
        self.processed_links = []
        self.enable_links = True

    def set_process_links(self,tf:bool):
        self.enable_links = tf

    # Returns articles. Must call run(...) first.
    def get_articles(self):
        return self.buffer
    
    # Gets articles by calling aggregator and process them by calling processor.
    def run(self):
        self.flush()
        self.__get_links()
        for aggregator in self.aggregators:
            print("Running aggregator...")
            obj, pl = self.__make(aggregator, self.processor)
            self.processed_links += pl
            self.buffer.append(obj)
            self.out()
            self.flush()
        print("Done executing aggregators")

    # Writes articles to a file. Must call run(...) first.
    def out(self, filename: str=""):
        if filename=="":
            filename = f"output/{int(time.time())}.json"
        lock_filename = f"{filename}.lock"
        if len(self.buffer) == 0:
            return
        
        with open(lock_filename, "w") as lock_file:
            pass

        with open(filename, "w") as f:
            json.dump(self.buffer, f,indent=4)

        self.__output_links()

        os.remove(lock_filename)

    def __output_links(self):
        if self.enable_links == False:
            return
        with open(self.links_file,"w") as output_file:
            for link in self.processed_links:
                output_file.write(f"{link[0]}:{link[1]}\n")
        self.processed_links = []

    # Erase articles from memory. Call after calling out(...) or get(...).
    def flush(self):
        self.buffer = []

    # Given aggregator and processor, retrives and processes articles,
    # records links for articles so that they won't be processed in the future,
    # and returns the results. Note that article links are only recorded
    # for the articles returned by this function.
    def __make(self, aggregator, processor):
        min_source_count = aggregator.get_min_source_count()
        articles = aggregator.get_articles()
        name = aggregator.get_name()
        cluster_distance_threshold = aggregator.get_cluster_distance_threshold()
        processor.set_cluster_distance_threshold(cluster_distance_threshold)
        processor.set_min_source_count(min_source_count)
        input_articles = [article for article in articles if article["link"] not in [link[1] for link in self.processed_links]]
        if len(input_articles) <= 0:
            return []
        processed_clusters, pl = processor.process_clusters(input_articles)
        result = {}
        result["aggregator"] = name
        result["clusters"] = processed_clusters
        return result, pl

    def __get_links(self):
        if self.enable_links == False:
            return
        links = []
        with open(self.links_file,"r") as input_file:
            for line in input_file:
                timestamp, link = line.strip().split(":",1)
                timestamp = int(timestamp)
                if timestamp >= self.link_limit:
                    links.append((timestamp,link))
        self.processed_links = links

#
# Append your aggregator to 'aggregators'
#
aggregators = [ESportsDramaAggregator(),NewsAggregator(),]
processor = ArticleProcessor()

master = Master(aggregators, processor)

while True:
    #master.set_process_links(False)
    master.run()
    time.sleep(1800*2)
