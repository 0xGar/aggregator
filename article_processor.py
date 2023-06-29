import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from transformers import logging, AutoTokenizer, TFAutoModel
from transformers import AutoModelForSeq2SeqLM
import nltk
from sklearn.cluster import AgglomerativeClustering
import time
from collections import defaultdict
from typing import Dict, List, Tuple
from transformers import pipeline

class ArticleProcessor:
    def __init__(self, min_source_count: int = 3, 
                summary_min_len: int = 4, 
                summary_max_len: int = 32,
                tag_num_beams: int = 2, 
                tag_min_length:int = 3,
                tag_max_length:int = 16,
                cluster_distance_threshold:int = 0.5):
        self.min_source_count = min_source_count #Minimum number of unique sources a cluster must have in order to be processed
        self.summary_min_len = summary_min_len #Maximum summary text length
        self.summary_max_len = summary_max_len #Minimum summary text length
        self.tag_num_beams = tag_num_beams #Number of beams for tag model
        self.tag_min_length = tag_min_length #Min length for tag model
        self.tag_max_length = tag_max_length #Max length for tag model
        self.cluster_distance_threshold = cluster_distance_threshold
        self.scaler = MinMaxScaler()
        logging.set_verbosity_error()
        nltk.download('punkt')

        # Embeddings
        self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-distilroberta-base-v2')
        self.model = TFAutoModel.from_pretrained('sentence-transformers/paraphrase-distilroberta-base-v2')

        # Summarizers
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

        # Tag generation
        self.tag_tokenizer = AutoTokenizer.from_pretrained("fabiochiu/t5-base-tag-generation")
        self.tag_model = AutoModelForSeq2SeqLM.from_pretrained("fabiochiu/t5-base-tag-generation")

    def set_min_source_count(self,count: int):
        self.min_source_count = count

    def set_cluster_distance_threshold(self,count: int=0.5):
        self.cluster_distance_threshold = count

    # Returns a list of articles where each article is by a different news source
    def remove_source_duplicates(self, array):
        unique_sources = set()
        filtered_array = []
        for item in array:
            if item["source"] not in unique_sources:
                unique_sources.add(item["source"])
                filtered_array.append(item)
        return filtered_array

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        # Set up & execute the model to generate embeddings
        inputs = self.tokenizer(texts, return_tensors='tf', padding=True, truncation=True)
        outputs = self.model(**inputs)
        embeddings = tf.reduce_mean(outputs.last_hidden_state, axis=1).numpy()
        return embeddings

    def generate_tags(self, cluster_articles: List[Dict[str, object]]) -> List[str]:
        print ("Creating tags")
        # Join descriptions into a single string
        text = ' '.join([article["description"] for article in cluster_articles])
        # Set up & execute the model to generate the tags
        inputs = self.tag_tokenizer([text], max_length=512, truncation=True, return_tensors="pt")
        output = self.tag_model.generate(**inputs, num_beams=self.tag_num_beams, do_sample=True, min_length=self.tag_min_length,
                                max_length = self.tag_max_length)
        decoded_output = self.tag_tokenizer.batch_decode(output, skip_special_tokens=True)[0]
        return list(set(decoded_output.strip().split(", ")))

    def generate_summaries(self, cluster_articles: List[Dict[str, object]]) -> str:
        # Join descriptions into a single string
        concatenated_descriptions = ' '.join([article["title"] for article in cluster_articles])
        print("Summarizing")
        # Run the model to get summarized text
        summary = self.summarizer(concatenated_descriptions, max_length=self.summary_max_len, min_length=self.summary_min_len, do_sample=False)[0]['summary_text']
        return summary.strip()

    def cluster_articles(self, articles: List[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
        clustering_results = defaultdict(list)

        # Create a list of article descriptions
        text = [article["title"] + " " + article["description"] for article in articles]
        # Create embeddings of the descriptions
        new_sentence_embeddings = self.create_embeddings(text)
        # Calculate cosine distances between descriptions
        new_distance_matrix = 1 - cosine_similarity(new_sentence_embeddings)
        # Normalize results
        new_normalized_distance_matrix = self.scaler.fit_transform(new_distance_matrix)
        # Use agglomerative clustering
        clustering = AgglomerativeClustering(n_clusters=None, affinity='precomputed', linkage='average', distance_threshold=self.cluster_distance_threshold)
        # Assign a cluster to the descriptions
        new_clusters = clustering.fit_predict(new_normalized_distance_matrix)

        # Create cluster map for the articles (the order of new_clusters is the same order
        # as articles, e.g., the cluster label in new_clusters[0]
        # refers to the article in article[0]
        for idx, label in enumerate(new_clusters):
            clustering_results[label].append(articles[idx])

        return clustering_results

    def process_clusters(self, input_articles) -> Tuple[List[Dict], List[str]]:
        processed_clusters = []
        processed_links = []
        # Generate clusters
        clustering_results = self.cluster_articles(input_articles)
        for label, articles in clustering_results.items():
            unique_sources = len(set(article["source"] for article in articles))
            if unique_sources >= self.min_source_count:
                # Sort by date
                articles = sorted(articles, key=lambda x: x['pub_date'], reverse=True)
                # Ensure each article is by a different news source
                filtered_articles = self.remove_source_duplicates(articles)
                # Record processed articles (their links)
                processed_links += [(article["pub_date"],article["link"]) for article in filtered_articles]
                # Generate tags for the cluster
                cluster_tags = self.generate_tags(filtered_articles)
                # Generate summary for the cluster
                cluster_summary = self.generate_summaries(filtered_articles)
                output_dict = {}
                output_dict["summary"] = cluster_summary
                output_dict["tags"] = cluster_tags
                output_dict["articles"] = filtered_articles
                processed_clusters.append(output_dict)
        # Sort the return array by the number of articles in each cluster
        processed_clusters = sorted(processed_clusters, key=lambda x: len(x["articles"]), reverse=True)
        return processed_clusters, processed_links