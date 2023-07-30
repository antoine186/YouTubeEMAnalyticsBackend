import sys
sys.path.append('ApplicationCore')
sys.path.append("ApplicationCore/analysis")

import pandas as pd
import os
from flask import Blueprint, request, make_response
import json
from gnews import GNews
from datetime import datetime, timedelta
from operator import attrgetter
# from app_start_helper import nn, model_max_characters_allowed, keyword_extractor_nn
from Utils.json_encoder import GenericJsonEncoder
# from app_start_helper import db
from sqlalchemy import text
from flask_mail import Mail, Message
from threading import Thread
# from app_start_helper import mail
from analytical_classes.emo_breakdown_result import EmoBreakdownResult
from Utils.text_divider import text_divider
from analysis.analytical_utils.get_emo_breakdown_percentage import get_emo_breakdown_percentage
from analysis.analytical_utils.get_emo_breakdown_from_tranches import get_emo_breakdown_from_tranches
from analytical_classes.emo_breakdown_result_metadata import EmoBreakdownResultMetadata
from analysis.analytical_utils.update_emo_breakdown_average import update_emo_breakdown_average
from Utils.results_sort_based_on_emo import results_sort_based_on_emo
from keybert import KeyBERT

from transformers import pipeline
keyword_extractor_nn = KeyBERT()

model_max_characters_allowed = 400
nn = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

os.chdir(r"D:\PythonProjects\NewsEmotionsExtraction\AdhocScripts")
print(os.getcwd())

df = pd.read_excel('ManualSocialMediaDataEntry.xlsx', header=None)

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

manual_data_list = []

for i in range(len(df)):
    manual_data_list.append(df.loc[i][0])

for result in manual_data_list:
    article = result
        
    if len(article) < model_max_characters_allowed:
        raw_emo_breakdown = nn(
            article)
        emo_breakdown = raw_emo_breakdown[0]

        raw_extracted_keywords = keyword_extractor_nn.extract_keywords(article, keyphrase_ngram_range=(1, 2), stop_words=None)

        extracted_keywords = raw_extracted_keywords
        extracted_keywords.sort(key=lambda word_pair: word_pair[1], reverse = True)

        emo_breakdown_percentage, most_emo_dict = get_emo_breakdown_percentage(emo_breakdown, result_counter, most_emo_dict)
        if emo_breakdown_average == None:
            emo_breakdown_average = emo_breakdown_percentage
        else:
            emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_percentage, emo_breakdown_average, result_counter)
        emo_breakdown_result = EmoBreakdownResult(
            'Dummy Title', 'Dummy Description', 'Dummy Publisher Title', 'Dummy Publishing Date', 'Dummy Link', emo_breakdown_percentage, extracted_keywords, result)
        emo_breakdown_results.append(emo_breakdown_result)
        result_counter += 1
    else:
        continue
        tranches_list = text_divider(article, model_max_characters_allowed)

        emo_breakdown_result, most_emo_dict = get_emo_breakdown_from_tranches(result_counter, most_emo_dict, tranches_list, nn, article, result, keyword_extractor_nn)

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

emo_breakdown_result_metadata = EmoBreakdownResultMetadata(emo_breakdown_results, 0, emo_breakdown_average, emo_breakdown_results[most_emo_dict['anger']['index']], 
        emo_breakdown_results[most_emo_dict['disgust']['index']], emo_breakdown_results[most_emo_dict['sadness']['index']], emo_breakdown_results[most_emo_dict['joy']['index']], 
        emo_breakdown_results[most_emo_dict['fear']['index']], emo_breakdown_results[most_emo_dict['surprise']['index']], emo_breakdown_results[most_emo_dict['neutral']['index']],
        self.search_input, self.search_start_date, self.search_end_date, '', top_5_anger, top_5_disgust, top_5_fear, top_5_joy, top_5_neutral, top_5_sadness, top_5_surprise)
