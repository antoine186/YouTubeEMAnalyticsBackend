import sys
sys.path.append("ApplicationCore/analysis")

from analytical_classes.emo_breakdown_result import EmoBreakdownResult
from Utils.text_divider import text_divider
from analysis.analytical_utils.get_emo_breakdown_percentage import get_emo_breakdown_percentage
from analysis.analytical_utils.get_emo_breakdown_from_tranches import get_emo_breakdown_from_tranches
from analytical_classes.emo_breakdown_result_metadata import EmoBreakdownResultMetadata
from analysis.analytical_utils.update_emo_breakdown_average import update_emo_breakdown_average
from Utils.results_sort_based_on_emo import results_sort_based_on_emo

class NewsClassifier:
    def __init__(self, nn, search_results, google_news, model_max_characters_allowed, keyword_extractor_nn, search_input, \
                 search_start_date, search_end_date):
        self.main_emo_classification_nn_model = nn.nn_model
        self.search_results = search_results
        self.google_news = google_news
        self.model_max_characters_allowed = model_max_characters_allowed
        self.keyword_extractor_nn = keyword_extractor_nn
        self.search_input = search_input
        self.search_start_date = search_start_date
        self.search_end_date = search_end_date

    def get_emo_percentage_breakdown_with_leading_results(self):
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

        result_counter = 0
        emo_breakdown_average = None

        try:
            for result in self.search_results:
                try:
                    article = self.google_news.get_full_article(result['url'])
                except:
                    nb_articles_skipped += 1
                    continue

                if (article == None):
                    nb_articles_skipped += 1
                    continue
                    
                if len(article.text) < self.model_max_characters_allowed:
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
                        article.title, result['description'], result['publisher']['title'], result['published date'], article.canonical_link, emo_breakdown_percentage, extracted_keywords, '')
                    emo_breakdown_results.append(emo_breakdown_result)
                    result_counter += 1
                else:
                    tranches_list = text_divider(article.text, self.model_max_characters_allowed)

                    emo_breakdown_result, most_emo_dict = get_emo_breakdown_from_tranches(result_counter, most_emo_dict, tranches_list, self.main_emo_classification_nn_model, article, result, self.keyword_extractor_nn)

                    if emo_breakdown_average == None:
                        emo_breakdown_average = emo_breakdown_result.emo_breakdown
                    else:
                        emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_result.emo_breakdown, emo_breakdown_average, result_counter)

                    emo_breakdown_results.append(emo_breakdown_result)

                    result_counter += 1

            top_5_anger = results_sort_based_on_emo(emo_breakdown_results, 'anger_percentage')
            top_5_disgust = results_sort_based_on_emo(emo_breakdown_results, 'disgust_percentage')
            top_5_fear = results_sort_based_on_emo(emo_breakdown_results, 'fear_percentage')
            top_5_joy = results_sort_based_on_emo(emo_breakdown_results, 'joy_percentage')
            top_5_neutral = results_sort_based_on_emo(emo_breakdown_results, 'neutral_percentage')
            top_5_sadness = results_sort_based_on_emo(emo_breakdown_results, 'sadness_percentage')
            top_5_surprise = results_sort_based_on_emo(emo_breakdown_results, 'surprise_percentage')

            emo_breakdown_result_metadata = EmoBreakdownResultMetadata(emo_breakdown_results, nb_articles_skipped, emo_breakdown_average, emo_breakdown_results[most_emo_dict['anger']['index']], 
                 emo_breakdown_results[most_emo_dict['disgust']['index']], emo_breakdown_results[most_emo_dict['sadness']['index']], emo_breakdown_results[most_emo_dict['joy']['index']], 
                 emo_breakdown_results[most_emo_dict['fear']['index']], emo_breakdown_results[most_emo_dict['surprise']['index']], emo_breakdown_results[most_emo_dict['neutral']['index']],
                 self.search_input, self.search_start_date, self.search_end_date, '', top_5_anger, top_5_disgust, top_5_fear, top_5_joy, top_5_neutral, top_5_sadness, top_5_surprise)
        
            return emo_breakdown_result_metadata

        except Exception as e:
            return None
