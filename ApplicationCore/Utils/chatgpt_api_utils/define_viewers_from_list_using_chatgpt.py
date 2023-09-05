from app_start_helper import chat_gpt_response_from_rapid_api, rapidapi_key, chatgpt4_rapidapi_url
import json
import requests

def define_viewers_from_list_using_chatgpt(raw_comments_tranch_list, llm_testing, generation_condition):
    prompt_string = 'What type of youtube viewer is this' + generation_condition + ': '
    for text in raw_comments_tranch_list:
        prompt_string += text + '. '

    if llm_testing:
        reply = 'Example ChatGPTs response'
    else:
        if chat_gpt_response_from_rapid_api:
            payload = { "query": prompt_string, "wordLimit":"300" }
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
                    model="gpt-3.5-turbo", messages=messages, max_tokens=300
                )
            
            reply = chat.choices[0].message.content

    return reply
