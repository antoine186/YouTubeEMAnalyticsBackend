import sys
sys.path.append("ApplicationCore/analysis")

from analytical_classes.emo_breakdown_result import EmoBreakdownResult
from Utils.text_divider import text_divider
from analysis.analytical_utils.get_emo_breakdown_percentage import get_emo_breakdown_percentage
from analysis.analytical_utils.get_emo_breakdown_from_tranches import get_emo_breakdown_from_tranches
from analytical_classes.emo_breakdown_result_metadata import EmoBreakdownResultMetadata
from analysis.analytical_utils.update_emo_breakdown_average import update_emo_breakdown_average

class TweetClassifier:
    def __init__(self, nn, tweet_results, model_max_characters_allowed, keyword_extractor_nn, current_date, tweeter, urlLink):
        self.main_emo_classification_nn_model = nn.nn_model
        self.tweet_results = tweet_results
        self.model_max_characters_allowed = model_max_characters_allowed
        self.keyword_extractor_nn = keyword_extractor_nn
        self.current_date = current_date
        self.tweeter = tweeter
        self.urlLink = urlLink

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
            for tweet in self.tweet_results:                
                raw_emo_breakdown = self.main_emo_classification_nn_model(
                    tweet)
                emo_breakdown = raw_emo_breakdown[0]

                raw_extracted_keywords = self.keyword_extractor_nn.nn_model.extract_keywords(tweet, keyphrase_ngram_range=(1, 2), stop_words=None)

                extracted_keywords = raw_extracted_keywords
                extracted_keywords.sort(key=lambda word_pair: word_pair[1], reverse = True)

                emo_breakdown_percentage, most_emo_dict = get_emo_breakdown_percentage(emo_breakdown, result_counter, most_emo_dict)
                if emo_breakdown_average == None:
                    emo_breakdown_average = emo_breakdown_percentage
                else:
                    emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_percentage, emo_breakdown_average, result_counter)
                emo_breakdown_result = EmoBreakdownResult(
                    tweet.title, 'A Tweet', self.tweeter, self.current_date, self.urlLink, emo_breakdown_percentage, extracted_keywords)
                emo_breakdown_results.append(emo_breakdown_result)
                result_counter += 1

            emo_breakdown_result_metadata = EmoBreakdownResultMetadata(emo_breakdown_results, nb_articles_skipped, emo_breakdown_average, emo_breakdown_results[most_emo_dict['anger']['index']], 
                 emo_breakdown_results[most_emo_dict['disgust']['index']], emo_breakdown_results[most_emo_dict['sadness']['index']], emo_breakdown_results[most_emo_dict['joy']['index']], 
                 emo_breakdown_results[most_emo_dict['fear']['index']], emo_breakdown_results[most_emo_dict['surprise']['index']], emo_breakdown_results[most_emo_dict['neutral']['index']],
                 'tweet standard input', self.current_date, self.current_date, '')
        
            return emo_breakdown_result_metadata

        except Exception as e:
            return None
