from app_start_helper import nn, model_max_characters_allowed, model_max_words_allowed
from analysis.analytical_utils.get_emo_breakdown_percentage import get_emo_breakdown_percentage
from analytical_classes.emo_breakdown_result_metadata import EmoBreakdownResultMetadata
from analysis.analytical_utils.update_emo_breakdown_average import update_emo_breakdown_average
from Utils.results_sort_based_on_emo import results_sort_based_on_emo
from analytical_classes.emo_breakdown_result import EmoBreakdownResult
from Utils.text_divider_by_word_count import text_divider_by_word_count
from analysis.analytical_utils.get_emo_breakdown_from_tranches import get_emo_breakdown_from_tranches
import copy
import math
from flask_mail import Mail, Message
from threading import Thread
from app_start_helper import mail

def emo_mine_from_list(text_list, video_title, published_date, publisher, video_link, thumbnail):
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

    print('Currently emo mining all comments for video ' + video_title)

    try:
        for text in text_list:
            if len(text.split()) < model_max_words_allowed and len(text) < model_max_characters_allowed:
                raw_emo_breakdown = nn.nn_model(text)
                emo_breakdown = raw_emo_breakdown[0]

                emo_breakdown_percentage, most_emo_dict = get_emo_breakdown_percentage(emo_breakdown, result_counter, most_emo_dict)

                if emo_breakdown_average == None:
                    emo_breakdown_average = emo_breakdown_percentage
                else:
                    emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_percentage, emo_breakdown_average, result_counter)

                emo_breakdown_result = EmoBreakdownResult(
                    video_title, 'Top Level Comment', publisher, published_date, video_link, emo_breakdown_percentage, '', text, thumbnail)
                emo_breakdown_results.append(emo_breakdown_result)
                result_counter += 1
            else:
                tranches_list = text_divider_by_word_count(text, model_max_words_allowed)

                emo_breakdown_result, most_emo_dict = get_emo_breakdown_from_tranches(result_counter, most_emo_dict, tranches_list, nn.nn_model,
                                                                                      video_title, 'Top Level Comment', publisher, published_date,
                                                                                      video_link, text, thumbnail)

                if emo_breakdown_average == None:
                    emo_breakdown_average = emo_breakdown_result.emo_breakdown
                else:
                    emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_result.emo_breakdown, emo_breakdown_average, result_counter)

                emo_breakdown_results.append(emo_breakdown_result)

                result_counter += 1

        sortable_emo_breakdown_results = copy.deepcopy(emo_breakdown_results)

        n = math.floor(len(text_list) / 4)

        top_n_anger = results_sort_based_on_emo(sortable_emo_breakdown_results, 'anger_percentage', n)
        top_n_disgust = results_sort_based_on_emo(sortable_emo_breakdown_results, 'disgust_percentage', n)
        top_n_fear = results_sort_based_on_emo(sortable_emo_breakdown_results, 'fear_percentage', n)
        top_n_joy = results_sort_based_on_emo(sortable_emo_breakdown_results, 'joy_percentage', n)
        top_n_neutral = results_sort_based_on_emo(sortable_emo_breakdown_results, 'neutral_percentage', n)
        top_n_sadness = results_sort_based_on_emo(sortable_emo_breakdown_results, 'sadness_percentage', n)
        top_n_surprise = results_sort_based_on_emo(sortable_emo_breakdown_results, 'surprise_percentage', n)

        emo_breakdown_result_metadata = EmoBreakdownResultMetadata(emo_breakdown_results, 0, emo_breakdown_average, emo_breakdown_results[most_emo_dict['anger']['index']], 
                emo_breakdown_results[most_emo_dict['disgust']['index']], emo_breakdown_results[most_emo_dict['sadness']['index']], emo_breakdown_results[most_emo_dict['joy']['index']], 
                emo_breakdown_results[most_emo_dict['fear']['index']], emo_breakdown_results[most_emo_dict['surprise']['index']], emo_breakdown_results[most_emo_dict['neutral']['index']],
                '', '', '', '', top_n_anger, top_n_disgust, top_n_fear, top_n_joy, top_n_neutral, top_n_sadness, top_n_surprise)
        
    except Exception as e:
        print(e)

        msg = Message()
        msg.subject = 'Error when applying emo AI to all top level comments for a single video'
        msg.recipients = ['antoine186@hotmail.com']
        msg.sender = 'noreply@emomachines.xyz'
        msg.body = str(e)

        Thread(target=mail.send(msg)).start()

    return emo_breakdown_result_metadata
