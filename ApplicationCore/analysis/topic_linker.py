import sys
sys.path.append("ApplicationCore/analysis")

from analytical_classes.emo_breakdown_result import EmoBreakdownResult
from Utils.text_divider import text_divider
from analysis.analytical_utils.get_emo_breakdown_percentage import get_emo_breakdown_percentage
from analysis.analytical_utils.get_emo_breakdown_from_tranches import get_emo_breakdown_from_tranches
from analytical_classes.emo_breakdown_result_metadata import EmoBreakdownResultMetadata
from analysis.analytical_utils.update_emo_breakdown_average import update_emo_breakdown_average
from sentence_transformers import SentenceTransformer, util

class TopicLinker:
    def __init__(self, nn, search_results_topic_1, search_results_topic_2, google_news, model_max_characters_allowed, keyword_extractor_nn, search_input, \
                 search_start_date, search_end_date):
        self.main_emo_classification_nn_model = nn.nn_model
        self.search_results_topic_1 = search_results_topic_1
        self.search_results_topic_2 = search_results_topic_2
        self.google_news = google_news
        self.model_max_characters_allowed = model_max_characters_allowed
        self.keyword_extractor_nn = keyword_extractor_nn
        self.search_input = search_input
        self.search_start_date = search_start_date
        self.search_end_date = search_end_date

    def find_linkage(self):
        nb_articles_skipped = 0
        emo_breakdown_results = []

        most_emo_dict = {
        'anger': {'score': 0, 'index': -1},
        'disgust': {'score': 0, 'index': -1},
        'joy': {'score': 0, 'index': -1},
        'sadness': {'score': 0, 'index': -1},
        'fear': {'score': 0, 'index': -1},
        'surprise': {'score': 0, 'index': -1},
        'neutral': {'score': 0, 'index': -1},
        }

        model = SentenceTransformer('all-MiniLM-L6-v2')

        search_results = self.search_results_topic_1 + self.search_results_topic_2

        result_counter = 0
        emo_breakdown_average = None

        articles_list_topic_1 = []
        articles_list_topic_2 = []

        topic_1_emo_breakdown = []
        topic_2_emo_breakdown = []

        article_counter = 0

        try:
            for result in search_results:
                try:
                    article_counter += 1
                    article = self.google_news.get_full_article(result['url'])
                except:
                    nb_articles_skipped += 1
                    continue

                if (article == None):
                    nb_articles_skipped += 1
                    continue
                
                if article_counter <= len(self.search_results_topic_1):
                    articles_list_topic_1.append(article.text)
                else:
                    articles_list_topic_2.append(article.text)

                if len(article.text) < self.model_max_characters_allowed:
                    """
                    input_ids = self.main_emo_classification_nn_tokenizer.encode(
                        article.text, return_tensors='pt')
                    output = self.main_emo_classification_nn_model.generate(
                        input_ids=input_ids)

                    decoded = [self.main_emo_classification_nn_tokenizer.decode(ids) for ids in output]
                    label = decoded[0]
                    """

                    raw_emo_breakdown = self.main_emo_classification_nn_model(
                        article.text)
                    emo_breakdown = raw_emo_breakdown[0]

                    raw_extracted_keywords = self.keyword_extractor_nn.nn_model.extract_keywords(article.text, keyphrase_ngram_range=(1, 2), stop_words=None)

                    extracted_keywords = raw_extracted_keywords
                    extracted_keywords.sort(key=lambda word_pair: word_pair[1], reverse = True)

                    emo_breakdown_percentage, most_emo_dict = get_emo_breakdown_percentage(emo_breakdown, result_counter, most_emo_dict)

                    if emo_breakdown_average == None:
                        emo_breakdown_average = emo_breakdown_percentage
                    else:
                        emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_percentage, emo_breakdown_average, result_counter)

                    emo_breakdown_result = EmoBreakdownResult(
                        article.title, result['description'], result['publisher']['title'], result['published date'], article.canonical_link, emo_breakdown_percentage, extracted_keywords)
                    emo_breakdown_results.append(emo_breakdown_result)
                    result_counter += 1

                    if article_counter <= len(self.search_results_topic_1):
                        topic_1_emo_breakdown.append(emo_breakdown_result)
                    else:
                        topic_2_emo_breakdown.append(emo_breakdown_result)
                    
                else:
                    tranches_list = text_divider(article.text, self.model_max_characters_allowed)

                    emo_breakdown_result, most_emo_dict = get_emo_breakdown_from_tranches(result_counter, most_emo_dict, tranches_list, self.main_emo_classification_nn_model, article, result, self.keyword_extractor_nn)

                    if emo_breakdown_average == None:
                        emo_breakdown_average = emo_breakdown_result.emo_breakdown
                    else:
                        emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_result.emo_breakdown, emo_breakdown_average, result_counter)

                    emo_breakdown_results.append(emo_breakdown_result)

                    result_counter += 1

                    if article_counter <= len(self.search_results_topic_1):
                        topic_1_emo_breakdown.append(emo_breakdown_result)
                    else:
                        topic_2_emo_breakdown.append(emo_breakdown_result)

            linked_articles = []
            forbidden_is = []
            forbidden_js = []

            for i in range(len(articles_list_topic_1)):
                for j in range(len(articles_list_topic_2)):
                    embeddings1 = model.encode(articles_list_topic_1[i], convert_to_tensor=True)
                    embeddings2 = model.encode(articles_list_topic_2[j], convert_to_tensor=True)

                    cosine_scores = util.cos_sim(embeddings1, embeddings2)

                    score = cosine_scores[0][0]

                    if score > 0.4:
                        if i not in forbidden_is:
                            linked_articles.append(topic_1_emo_breakdown[i])
                            forbidden_is.append(i)
                            forbidden_is = [*set(forbidden_is)]

                        if j not in forbidden_js:
                            linked_articles.append(topic_2_emo_breakdown[j])
                            forbidden_js.append(j)
                            forbidden_js = [*set(forbidden_js)]
        
            return linked_articles

        except Exception as e:
            return None