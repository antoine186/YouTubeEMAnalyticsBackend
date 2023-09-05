from Utils.list_divide_into_lists import list_divide_into_lists
from app_start_helper import llm_testing, number_of_comments_in_tranch_to_generate_video_description, chat_gpt_response_from_rapid_api, chatgpt4_rapidapi_url, db, rapidapi_key
from Utils.chatgpt_api_utils.define_viewers_from_list_using_chatgpt import define_viewers_from_list_using_chatgpt
import json
import requests
import openai
from sqlalchemy import text

def define_viewers_in_video_using_chatgpt(raw_comments, previous_video_analysis_id, update_video_description):
    try:
        raw_comments_tranch_lists = list_divide_into_lists(raw_comments, number_of_comments_in_tranch_to_generate_video_description)

        overall_viewer_descriptions = ''
        for raw_comments_tranch_list in raw_comments_tranch_lists:
            tranch_list_response = define_viewers_from_list_using_chatgpt(raw_comments_tranch_list, llm_testing, '')
            overall_viewer_descriptions += tranch_list_response + '. '

        prompt_string = 'Please summarise: '
        prompt_string += overall_viewer_descriptions

        if llm_testing:
            reply = 'Example ChatGPT response'
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

        if update_video_description:
            update_who_are_viewers_approximated_sp = 'CALL youtube_schema.update_who_are_viewers_approximated(:who_are_viewers_approximated,:previous_video_analysis_id)'
            db.session.execute(text(update_who_are_viewers_approximated_sp),
                                        {'who_are_viewers_approximated': reply, 'previous_video_analysis_id': previous_video_analysis_id})
            db.session.commit()
        else:
            add_who_are_viewers_approximated_sp = 'CALL youtube_schema.add_who_are_viewers_approximated(:previous_video_analysis_id,:who_are_viewers_approximated)'
            db.session.execute(text(add_who_are_viewers_approximated_sp),
                                        {'previous_video_analysis_id': previous_video_analysis_id, 'who_are_viewers_approximated': reply})
            db.session.commit()

        return reply
    except Exception as e:
        print(e)
