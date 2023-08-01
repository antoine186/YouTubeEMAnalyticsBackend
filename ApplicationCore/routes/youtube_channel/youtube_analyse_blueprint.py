from flask import Blueprint, request, make_response
import json
from app_start_helper import db
from sqlalchemy import text
from Utils.json_encoder import GenericJsonEncoder
from app_start_helper import youtube_object, rapidapi_key
from app_start_helper import nn, model_max_characters_allowed
from Utils.youtube_api_utils.raw_comments_grab_append import raw_comments_grab_append
from flask_mail import Mail, Message
from threading import Thread
from app_start_helper import mail
import requests

youtube_analyse_blueprint = Blueprint('youtube_analyse_blueprint', __name__)

@youtube_analyse_blueprint.route('/api/channelUrl', methods=['POST'])
def youtube_analyse():
    payload = request.data
    payload = json.loads(payload)

    print('YouTube channel analysis started!')

    try:
        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        """
        channel = youtube_object.channels().list(
            id = payload['channelInput'],
            part = 'contentDetails',
            maxResults = 10
        ).execute()
        """

        url = "https://youtube-v31.p.rapidapi.com/channels"

        querystring = {"part":"contentDetails","id":payload['channelInput']}

        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "youtube-v31.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        channel = json.loads(response.text)

        main_uploads_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        playlist_content = youtube_object.playlistItems().list(
            playlistId = main_uploads_id,
            part = 'snippet,contentDetails,id'
        ).execute()

        check_previous_channel_analysis = 'SELECT youtube_schema.check_previous_channel_analysis(:user_id,:channel_id)'

        previous_channel_analysis_id = db.session.execute(text(check_previous_channel_analysis), {'user_id': user_id[0][0], 'channel_id': payload['channelInput']}).fetchall()

        if previous_channel_analysis_id[0][0] == None:
            add_channel_analysis_sp = 'CALL youtube_schema.add_channel_analysis(:user_id,:_channel_id)'
            db.session.execute(text(add_channel_analysis_sp), {'user_id': user_id[0][0], '_channel_id': payload['channelInput']})
            db.session.commit()

            check_previous_channel_analysis = 'SELECT youtube_schema.check_previous_channel_analysis(:user_id,:channel_id)'
            previous_channel_analysis_id = db.session.execute(text(check_previous_channel_analysis), {'user_id': user_id[0][0], 'channel_id': payload['channelInput']}).fetchall()

        raw_comments_grab_append(playlist_content, user_id, previous_channel_analysis_id)

        while 'nextPageToken' in playlist_content.keys() and playlist_content['nextPageToken'] != '':
                playlist_content = youtube_object.playlistItems().list(
                    playlistId = main_uploads_id,
                    part = 'snippet,contentDetails,id',
                    pageToken = playlist_content['nextPageToken']
                ).execute()

                raw_comments_grab_append(playlist_content, user_id, previous_channel_analysis_id)

        print('YouTube channel analysis done!')

        operation_response = {
            "operation_success": True,
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
                 e.status_code
            },
            "error_message": "YouTube API quota exceeded"
        }
        response = make_response(json.dumps(operation_response))

        msg = Message()
        msg.subject = 'Error when initiating top level analysis of a YouTube channel'
        msg.recipients = ['antoine186@hotmail.com']
        msg.sender = 'noreply@emomachines.xyz'
        msg.body = str(e)

        Thread(target=mail.send(msg)).start()

        return response
