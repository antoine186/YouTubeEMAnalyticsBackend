from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder
from models.previous_video_analysis import PreviousVideoAnalysis

youtube_retrieve_channel_results_blueprint = Blueprint('youtube_retrieve_channel_results_blueprint', __name__)

@youtube_retrieve_channel_results_blueprint.route('/api/youtube-retrieve-channel-results', methods=['POST'])
def youtube_analyse():
    payload = request.data
    payload = json.loads(payload)

    check_previous_channel_analysis = 'SELECT youtube_schema.check_previous_channel_analysis(:user_id,:channel_id)'

    previous_channel_analysis_id = db.session.execute(text(check_previous_channel_analysis), {'user_id': '291', 'channel_id': 'UCHL9bfHTxCMi-7vfxQ-AYtg'}).fetchall()

    top_5_videos = []

    if previous_channel_analysis_id[0][0] == None:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": "No previous channel analysis to retrieve"
        }
        response = make_response(json.dumps(operation_response))
    
        return response

    previous_channel_analysis_ids = [id[0] for id in previous_channel_analysis_id] 

    for id in previous_channel_analysis_ids:
        previous_video_analyses = PreviousVideoAnalysis.query.filter(PreviousVideoAnalysis.previous_channel_analysis_id == id).all()

        video_counter = 0
        for previous_video_analysis in previous_video_analyses:
            if video_counter < 5:
                top_5_videos.append(json.loads(previous_video_analysis.previous_video_analysis_json))
            else:
                break
            video_counter += 1

    operation_response = {
        "operation_success": True,
        "responsePayload": {
             'top_5_videos': top_5_videos
        },
    }
    response = make_response(json.dumps(operation_response))

    return response
