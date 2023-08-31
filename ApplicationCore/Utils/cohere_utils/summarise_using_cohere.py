from Utils.emo_icons_to_strings import emo_icons_to_strings
from flask import Blueprint, request, make_response
import json
from app_start_helper import llm_testing, cohere_client

def summarise_using_cohere(top_10_shuffled_comments, emo_icon):
    prompt_string = 'Please summarise what made you ' + emo_icons_to_strings[emo_icon] + ' when watching this video in not more than 300 words (speak in the first-person): '
    for comment in top_10_shuffled_comments:
        prompt_string += comment['text'] + '. '

    if llm_testing:
        reply = 'Example cohere response'
    else:
        response = cohere_client.generate(
            model='command-xlarge-nightly',
            prompt=prompt_string,
            max_tokens=300,
            temperature=0.9,
            k=0,
            p=0.75,
            frequency_penalty=0,
            presence_penalty=0,
            stop_sequences=[],
            return_likelihoods='NONE')
        
        reply = response.generations[0].text

    return reply
