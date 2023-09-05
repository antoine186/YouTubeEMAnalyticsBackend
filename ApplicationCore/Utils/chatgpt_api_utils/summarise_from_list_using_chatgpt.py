import openai
from app_start_helper import rapidapi_key, chatgpt4_rapidapi_url, chat_gpt_response_from_rapid_api
import json
import requests

def summarise_from_list_using_chatgpt(list_to_summarise, llm_testing):
    prompt_string = 'Please summarise the following video comments: '
    for text in list_to_summarise:
        prompt_string += text + '. '

    if llm_testing:
        reply = 'Example ChatGPTs response'
    else:
        if chat_gpt_response_from_rapid_api:
            payload = { "query": prompt_string, "wordLimit":"50" }
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": "chatgpt-gpt4-ai-chatbot.p.rapidapi.com"
            }

            response = requests.post(chatgpt4_rapidapi_url, json=payload, headers=headers)

            response = json.loads(response.text)
            reply = response['response']
        else:
            messages = [ {"role": "system", "content": prompt_string} ]
            chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages, max_tokens=50
                )
            
            reply = chat.choices[0].message.content

    return reply
