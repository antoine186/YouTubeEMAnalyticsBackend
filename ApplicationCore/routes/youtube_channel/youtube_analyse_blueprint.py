from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder
from app_start_helper import youtube_object
from app_start_helper import nn, model_max_characters_allowed
from Utils.youtube_api_utils.raw_comments_grab_append import raw_comments_grab_append

youtube_analyse_blueprint = Blueprint('youtube_analyse_blueprint', __name__)

@youtube_analyse_blueprint.route('/api/channelUrl', methods=['POST'])
def youtube_analyse():
    payload = request.data
    payload = json.loads(payload)

    try:
        channel = youtube_object.channels().list(
            id = payload['channelInput'],
            part = 'contentDetails',
            maxResults = 10
        ).execute()

        main_uploads_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        playlist_content = youtube_object.playlistItems().list(
            playlistId = main_uploads_id,
            part = 'snippet,contentDetails,id'
        ).execute()

        raw_comments_grab_append(playlist_content, payload['username'])

        print()
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
