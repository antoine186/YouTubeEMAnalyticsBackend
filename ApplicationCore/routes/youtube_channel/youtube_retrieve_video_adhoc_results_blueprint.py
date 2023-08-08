from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder
from models.previous_video_analysis import PreviousVideoAnalysis
from models.top_n_emotions import TopNEmotions

youtube_retrieve_video_adhoc_results_blueprint = Blueprint('youtube_retrieve_video_adhoc_results_blueprint', __name__)

@youtube_retrieve_video_adhoc_results_blueprint.route('/api/youtube-retrieve-video-adhoc-results', methods=['POST'])
def youtube_retrieve_video_adhoc_results():
    payload = request.data
    payload = json.loads(payload)

    get_user_id = 'SELECT user_schema.get_user_id(:username)'

    user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

    try:
        check_user_searched_video = 'SELECT youtube_schema.check_user_searched_video(:user_id)'
        video_id = db.session.execute(text(check_user_searched_video), {'user_id': user_id[0][0]}).fetchall()

        check_previous_video_analysis_simplified = 'SELECT youtube_schema.check_previous_video_analysis_simplified(:video_id)'
        previous_video_analysis_id = db.session.execute(text(check_previous_video_analysis_simplified), {'video_id': video_id[0][0]}).fetchall()

        check_video_analysis_loading_status = 'SELECT youtube_schema.check_video_analysis_loading_status(:previous_video_analysis_id)'
        video_analysis_loading_status = db.session.execute(text(check_video_analysis_loading_status), {'previous_video_analysis_id': previous_video_analysis_id[0][0]}).fetchall()

        if video_analysis_loading_status[0][0] != None:
            if check_video_analysis_loading_status == 'active':
                operation_response = {
                    "operation_success": False,
                    "responsePayload": {
                    },
                    "error_message": ""
                }
                response = make_response(json.dumps(operation_response))
                return response
        else:
            operation_response = {
                "operation_success": False,
                "responsePayload": {
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
        return response
    
    get_previous_video_analysis = 'SELECT youtube_schema.get_previous_video_analysis(:previous_video_analysis_id)'
    previous_video_analysis = db.session.execute(text(get_previous_video_analysis), {'previous_video_analysis_id': previous_video_analysis_id[0][0]}).fetchall()
    previous_video_analysis = json.loads(previous_video_analysis[0][0])

    previous_top_n_emotions = TopNEmotions.query.filter(TopNEmotions.previous_video_analysis_id == previous_video_analysis_id[0][0]).all()

    top_n_anger = json.loads(previous_top_n_emotions[0].top_n_anger)
    top_n_disgust = json.loads(previous_top_n_emotions[0].top_n_disgust)
    top_n_fear = json.loads(previous_top_n_emotions[0].top_n_fear)
    top_n_joy = json.loads(previous_top_n_emotions[0].top_n_joy)
    top_n_neutral = json.loads(previous_top_n_emotions[0].top_n_neutral)
    top_n_sadness = json.loads(previous_top_n_emotions[0].top_n_sadness)
    top_n_surprise = json.loads(previous_top_n_emotions[0].top_n_surprise)

    operation_response = {
        "operation_success": True,
        "responsePayload": {
             'video_data': previous_video_analysis,
             'top_n_anger': top_n_anger,
             'top_n_disgust': top_n_disgust,
             'top_n_fear': top_n_fear,
             'top_n_joy': top_n_joy,
             'top_n_neutral': top_n_neutral,
             'top_n_sadness': top_n_sadness,
             'top_n_surprise': top_n_surprise,
             'average_emo_breakdown': previous_video_analysis['average_emo_breakdown']
        },
    }
    response = make_response(json.dumps(operation_response))

    return response
