from app_start_helper import number_of_comments_in_tranch_to_generate_video_description, llm_testing, cohere_client, db
from sqlalchemy import text
from Utils.list_divide_into_lists import list_divide_into_lists
from Utils.cohere_utils.summarise_from_list_using_cohere import summarise_from_list_using_cohere

def generate_video_description_using_cohere(raw_comments, previous_video_analysis_id, update_video_description):
    try:
        raw_comments_tranch_lists = list_divide_into_lists(raw_comments, number_of_comments_in_tranch_to_generate_video_description)

        overall_summarised_comments = ''
        for raw_comments_tranch_list in raw_comments_tranch_lists:
            tranch_list_summary = summarise_from_list_using_cohere(raw_comments_tranch_list, cohere_client, llm_testing)
            overall_summarised_comments += tranch_list_summary + '. '

        prompt_string = 'Please summarise what the video is about using the following comments it got: '
        prompt_string += overall_summarised_comments

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
