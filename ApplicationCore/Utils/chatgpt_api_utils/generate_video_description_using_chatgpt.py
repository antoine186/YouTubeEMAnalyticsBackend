from app_start_helper import number_of_comments_in_tranch_to_generate_video_description, llm_testing, db
from sqlalchemy import text
from Utils.list_divide_into_lists import list_divide_into_lists
from Utils.chatgpt_api_utils.summarise_from_list_using_chatgpt import summarise_from_list_using_chatgpt
import openai

def generate_video_description_using_chatgpt(raw_comments, previous_video_analysis_id, update_video_description):
    try:
        raw_comments_tranch_lists = list_divide_into_lists(raw_comments, number_of_comments_in_tranch_to_generate_video_description)

        overall_summarised_comments = ''
        for raw_comments_tranch_list in raw_comments_tranch_lists:
            tranch_list_summary = summarise_from_list_using_chatgpt(raw_comments_tranch_list, llm_testing)
            overall_summarised_comments += tranch_list_summary + '. '

        prompt_string = 'Please summarise without mentioning viewers what the video is about using the following comments it got: '
        prompt_string += overall_summarised_comments

        if llm_testing:
            reply = 'Example ChatGPT response'
        else:
            messages = [ {"role": "system", "content": prompt_string} ]
            chat = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", messages=messages, max_tokens=300
                )
            
            reply = chat.choices[0].message.content

        if update_video_description:
            update_video_approximated_description_sp = 'CALL youtube_schema.update_video_approximated_description(:approximated_video_description,:previous_video_analysis_id)'
            db.session.execute(text(update_video_approximated_description_sp),
                                        {'approximated_video_description': reply, 'previous_video_analysis_id': previous_video_analysis_id})
            db.session.commit()
        else:
            add_video_approximated_description_sp = 'CALL youtube_schema.add_video_approximated_description(:previous_video_analysis_id,:approximated_video_description)'
            db.session.execute(text(add_video_approximated_description_sp),
                                        {'previous_video_analysis_id': previous_video_analysis_id, 'approximated_video_description': reply})
            db.session.commit()

        return reply
    except Exception as e:
        print(e)
