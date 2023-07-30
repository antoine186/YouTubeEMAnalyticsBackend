from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from gnews import GNews
from datetime import datetime, timedelta
from operator import attrgetter
from app_start_helper import nn, model_max_characters_allowed, keyword_extractor_nn
from analysis.news_classifier import NewsClassifier
from Utils.json_encoder import GenericJsonEncoder
from Utils.month_array import month_strings

progression_charting_blueprint = Blueprint('progression_charting_blueprint', __name__)

@progression_charting_blueprint.route('/api/progression-charting', methods=['POST'])
def progression_charting():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    add_still_charting_sp = 'CALL search_schema.add_still_charting(:user_id,:still_charting)'

    db.session.execute(text(add_still_charting_sp), {'user_id': user_id[0][0], 'still_charting': True})

    db.session.commit()

    try:
        search_end_date = datetime.strptime(payload['dateInput'], '%Y-%m-%d')

        emo_breakdown_result_metadata_dict = {
            "emo_breakdown_result_metadata_1": emo_month_calculator(search_end_date, 0, payload['searchInput']),
            "emo_breakdown_result_metadata_2": emo_month_calculator(search_end_date, 1, payload['searchInput']),
            "emo_breakdown_result_metadata_3": emo_month_calculator(search_end_date, 2, payload['searchInput']),
            "emo_breakdown_result_metadata_4": emo_month_calculator(search_end_date, 3, payload['searchInput']),
            "emo_breakdown_result_metadata_5": emo_month_calculator(search_end_date, 4, payload['searchInput']),
            "emo_breakdown_result_metadata_6": emo_month_calculator(search_end_date, 5, payload['searchInput'])
        }

        emo_breakdown_result_metadata_dict_json_data = json.dumps(emo_breakdown_result_metadata_dict, indent=4, cls=GenericJsonEncoder)

        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        delete_previous_chart_result_sp = 'CALL search_schema.delete_previous_chart_result(:user_id)'

        db.session.execute(text(delete_previous_chart_result_sp), {'user_id': user_id[0][0]})

        db.session.commit()

        save_chart_result_sp = 'CALL search_schema.save_chart_result(:user_id,:previous_chart_result_json)'

        db.session.execute(text(save_chart_result_sp), {'user_id': user_id[0][0], 'previous_chart_result_json': emo_breakdown_result_metadata_dict_json_data})

        db.session.commit()

        delete_still_charting_sp = 'CALL search_schema.delete_still_charting(:user_id)'

        db.session.execute(text(delete_still_charting_sp), {'user_id': user_id[0][0]})

        db.session.commit()

        operation_response = {
            "operation_success": True,
            "responsePayload": {
                "emo_breakdown_result_metadata_dict": json.loads(emo_breakdown_result_metadata_dict_json_data)
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
    
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))

        delete_still_charting_sp = 'CALL search_schema.delete_still_charting(:user_id)'

        db.session.execute(text(delete_still_charting_sp), {'user_id': user_id[0][0]})

        db.session.commit()

        return response

def emo_month_calculator(yesterdays_date, months_going_back, searchInput):
    try:
        search_end_date = yesterdays_date - timedelta(days=30*months_going_back)
        search_start_date = yesterdays_date - timedelta(days=30*(months_going_back)+30)

        attributes = ('year', 'month', 'day')

        search_end_date = attrgetter(*attributes)(search_end_date)
        search_start_date = attrgetter(*attributes)(search_start_date)

        emo_month = month_strings[search_end_date[1]-1]
        emo_year = search_end_date[0]

        google_news = GNews(language='en', country='US', start_date = search_start_date, end_date = search_end_date, max_results = 10)
        results = google_news.get_news(searchInput)

        news_classifier = NewsClassifier(nn, results, google_news, model_max_characters_allowed, keyword_extractor_nn, searchInput, \
                                        search_start_date, search_end_date)
        emo_breakdown_result_metadata = news_classifier.get_emo_percentage_breakdown_with_leading_results()

        emo_breakdown_result_metadata.emo_month = emo_month
        emo_breakdown_result_metadata.emo_year = emo_year

        return emo_breakdown_result_metadata
    except Exception as e:
        print(e)
