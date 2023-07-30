from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from gnews import GNews
from datetime import datetime, timedelta
from operator import attrgetter
from app_start_helper import nn, model_max_characters_allowed, keyword_extractor_nn
from analysis.topic_linker import TopicLinker
from Utils.json_encoder import GenericJsonEncoder
from analysis.analytical_utils.update_emo_breakdown_average import update_emo_breakdown_average

linking_blueprint = Blueprint('linking_blueprint', __name__)

@linking_blueprint.route('/api/linking-topics', methods=['POST'])
def linking_topics():
    try:
        payload = request.data
        payload = json.loads(payload)

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        attributes = ('year', 'month', 'day')

        search_end_date = datetime.strptime(payload['dateInput'], '%Y-%m-%d')
        search_start_date = search_end_date - timedelta(days=30)

        search_end_date = attrgetter(*attributes)(search_end_date)
        search_start_date = attrgetter(*attributes)(search_start_date)

        google_news = GNews(language='en', country='US', start_date = search_start_date, end_date = search_end_date, max_results = 20)

        results_topic_1 = google_news.get_news(payload['linkingInput1'])

        results_topic_2 = google_news.get_news(payload['linkingInput2'])

        results_topic_1.append(results_topic_2)

        google_news_seed = GNews(language='en', country='US', start_date = search_start_date, end_date = search_end_date, max_results = 5)

        results_seed = google_news_seed.get_news(payload['linkingInput1'] + ' ' + payload['linkingInput2'])

        topic_linker = TopicLinker(nn, results_seed, results_topic_1, google_news, model_max_characters_allowed, keyword_extractor_nn, payload['linkingInput1'] + ' ' + payload['linkingInput2'], \
                                        search_start_date, search_end_date)
        topic_linking_results = topic_linker.find_linkage()

        if len(topic_linking_results) == 0:
            operation_response = {
            "operation_success": False,
                "responsePayload": {
                },
                "error_message": ""
            }
            response = make_response(json.dumps(operation_response))
            return response

        result_counter = 0

        emo_breakdown_average = None
        for i in range(len(topic_linking_results)):
            if emo_breakdown_average == None:
                emo_breakdown_average = topic_linking_results[i].emo_breakdown
            else:
                emo_breakdown_average = update_emo_breakdown_average(topic_linking_results[i].emo_breakdown, emo_breakdown_average, result_counter)

            result_counter += 1

        linking_emo_breakdown_result_metadata_dict = {
            "emo_breakdown_average": emo_breakdown_average,
            "topic_linking_results": topic_linking_results,
            "linkingInput1": payload['linkingInput1'],
            "linkingInput2": payload['linkingInput2'],
            "dateInput": payload['dateInput']
        }

        linking_emo_breakdown_result_metadata_dict_json_data = json.dumps(linking_emo_breakdown_result_metadata_dict, indent=4, cls=GenericJsonEncoder)

        delete_linking_result_sp = 'CALL search_schema.delete_linking_result(:user_id)'

        db.session.execute(text(delete_linking_result_sp), {'user_id': user_id[0][0]})

        db.session.commit()

        add_linking_result_sp = 'CALL search_schema.add_linking_result(:user_id,:previous_linking_result)'

        db.session.execute(text(add_linking_result_sp), {'user_id': user_id[0][0], 'previous_linking_result': linking_emo_breakdown_result_metadata_dict_json_data})

        db.session.commit()

        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "linking_emo_breakdown_result_metadata_dict_json_data": linking_emo_breakdown_result_metadata_dict_json_data
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response

    except Exception as e:
        response = make_response(json.dumps('Error'))

        return response
