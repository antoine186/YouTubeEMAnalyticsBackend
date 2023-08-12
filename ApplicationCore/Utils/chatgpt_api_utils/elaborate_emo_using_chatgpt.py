import openai
from Utils.emo_icons_to_strings import emo_icons_to_strings
from flask import Blueprint, request, make_response
import json
from app_start_helper import chat_gpt_testing

def elaborate_emo_using_chatgpt(top_10_shuffled_comments, emo_icon):
    prompt_string = ''
    if emo_icons_to_strings[emo_icon] == 'happy':
        prompt_string = 'Provide tips in less than 300 words for video improvements for more views and greater emotional engagement '
        prompt_string += '(making audience even happier). Your tips should be drawn from the following comments they made: '
    elif emo_icons_to_strings[emo_icon] == 'angry':
        prompt_string = 'Provide tips in less than 300 words for video improvements for more views and greater emotional engagement '
        prompt_string += '(making audience angrier or less angry depending on how appropriate). Your tips should be drawn from the following comments they made: '
    elif emo_icons_to_strings[emo_icon] == 'disgusted':
        prompt_string = 'Provide tips in less than 300 words for video improvements for more views and greater emotional engagement '
        prompt_string += '(by stimulating their morbid curiosity about anything disgusting). Your tips should be drawn from the following comments they made: '
    elif emo_icons_to_strings[emo_icon] == 'sad':
        prompt_string = 'Provide tips in less than 300 words for video improvements for more views and greater emotional engagement '
        prompt_string += '(keeping in mind that sadness reveals whats really important to the audience). Your tips should be drawn from the following comments they made: '
    elif emo_icons_to_strings[emo_icon] == 'fearful':
        prompt_string = 'Provide tips in less than 300 words for video improvements for more views and greater emotional engagement '
        prompt_string += '(by thrilling the audience with fear). Your tips should be drawn from the following comments they made: '
    elif emo_icons_to_strings[emo_icon] == 'surprised':
        prompt_string = 'Provide tips in less than 300 words for video improvements for more views and greater emotional engagement '
        prompt_string += '(by further surprising and amazing them). Your tips should be drawn from the following comments they made: '
    elif emo_icons_to_strings[emo_icon] == 'feeling neutral':
        prompt_string = 'Provide tips in less than 300 words for video improvements for more views and greater emotional engagement '
        prompt_string += '(keeping in mind that this audience isnt impressed with the video). Your tips should be drawn from the following comments they made: '
    
    for comment in top_10_shuffled_comments:
        prompt_string += comment['text'] + '. '

    if chat_gpt_testing:
        reply = 'Example chatgpt response'
    else:
        messages = [ {"role": "system", "content": prompt_string} ]
        chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
        
        reply = chat.choices[0].message.content

    return reply
