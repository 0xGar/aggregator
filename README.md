# aggregator
News article aggregator

This Python script groups similar news stories together across various RSS feeds at a set interval, outputting the results into a file. It uses the sentence-transformers/paraphrase-distilroberta-base-v2 model from Hugging Face to extract summaries, which are then used to create article clusters via agglomerative clustering.

'aggregator_esports.drama.py" and "aggregator_mainstream_news.py" are provided as examples. These files specify RSS feeds,
and settings specifying how the feeds should be processed. For example, the latter mentioned file specifies mainstream RSS news feeds. In addition, it specifies the cluster distance for grouping, and the minimum number of items that group must have (which are news articles from separate sources) in order to be included in the output results.

Each general topic (e.g., politics, health, science, mainstream news, esports, etc,.) should have its own aggregator file. To do so, 1) copy either "aggregator_esports.drama.py" or "aggregator_mainstream_news.py" and modify as needed, and then 2) import the file into run.py and then append to the 'aggregators' array. See comments in that file for further instructions.
