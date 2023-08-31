import openai
from Utils.emo_icons_to_strings import emo_icons_to_strings
from flask import Blueprint, request, make_response
import json
from app_start_helper import llm_testing

def summarise_using_chatgpt(top_10_shuffled_comments, emo_icon):
    #prompt_string = 'Please summarise what made viewers of this youtube video ' + emo_icons_to_strings[emo_icon] + ' in not more than 300 words: '
    prompt_string = 'Please summarise what made you ' + emo_icons_to_strings[emo_icon] + ' when watching this video in not more than 300 words (speak in the first-person): '
    for comment in top_10_shuffled_comments:
        prompt_string += comment['text'] + '. '

    if llm_testing:
        reply = 'Example chatgpt response'
    else:
        messages = [ {"role": "system", "content": prompt_string} ]
        chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
        
        reply = chat.choices[0].message.content

    return reply
