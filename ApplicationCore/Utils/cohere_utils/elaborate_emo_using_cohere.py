import cohere
from Utils.emo_icons_to_strings import emo_icons_to_strings
from flask import Blueprint, request, make_response
import json
from app_start_helper import llm_testing, cohere_client

def elaborate_emo_using_cohere(top_10_shuffled_comments, emo_icon):
    prompt_string = ''
    if emo_icons_to_strings[emo_icon] == 'happy':
        #prompt_string = 'Use the following feedback to suggest video improvements (speak in first-person and as the happy person giving feedback, not as the person receiving it): '
        prompt_string = 'Suggest video improvements using the following feedback: '
    elif emo_icons_to_strings[emo_icon] == 'angry':
        #prompt_string = 'Use the following feedback to suggest video improvements (speak in first-person and as the angry person giving feedback, not as the person receiving it): '
         prompt_string = 'Suggest video improvements using the following feedback: '
    elif emo_icons_to_strings[emo_icon] == 'disgusted':
        #prompt_string = 'Use the following feedback to suggest video improvements (speak in first-person and as the disgusted person giving feedback, not as the person receiving it): '
         prompt_string = 'Suggest video improvements using the following feedback: '
    elif emo_icons_to_strings[emo_icon] == 'sad':
        #prompt_string = 'Use the following feedback to suggest video improvements (speak in first-person and as the sad person giving feedback, not as the person receiving it): '
         prompt_string = 'Suggest video improvements using the following feedback: '
    elif emo_icons_to_strings[emo_icon] == 'fearful':
        #prompt_string = 'Use the following feedback to suggest video improvements (speak in first-person and as the fearful person giving feedback, not as the person receiving it): '
         prompt_string = 'Suggest video improvements using the following feedback: '
    elif emo_icons_to_strings[emo_icon] == 'surprised':
        #prompt_string = 'Use the following feedback to suggest video improvements (speak in first-person and as the astonished person giving feedback, not as the person receiving it): '
         prompt_string = 'Suggest video improvements using the following feedback: '
    elif emo_icons_to_strings[emo_icon] == 'feeling neutral':
        #prompt_string = 'Use the following feedback to suggest video improvements (speak in first-person and as the unimpressed person giving feedback, not as the person receiving it): '
         prompt_string = 'Suggest video improvements using the following feedback: '
    
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
