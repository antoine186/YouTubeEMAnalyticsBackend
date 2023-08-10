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
from Utils.youtube_api_utils.unpack_youtube_top_level_comments_yt_api import unpack_youtube_top_level_comments_yt_api
from Utils.emo_utils.emo_mine_from_list_adhoc import emo_mine_from_list_adhoc
from datetime import datetime, timedelta, date
import copy

youtube_video_adhoc_analyse_blueprint = Blueprint('youtube_video_adhoc_analyse_blueprint', __name__)

@youtube_video_adhoc_analyse_blueprint.route('/api/youtube-video-adhoc-analyse', methods=['POST'])
def youtube_analyse():
    payload = request.data
    payload = json.loads(payload)

    print('YouTube video adhoc analysis started!')

    try:
        get_user_id = 'SELECT user_schema.get_user_id(:username)'

        user_id = db.session.execute(text(get_user_id), {'username': payload['username']}).fetchall()

        check_user_searched_video = 'SELECT youtube_schema.check_user_searched_video(:user_id)'
        video_id = db.session.execute(text(check_user_searched_video), 
                                                            {'user_id': user_id[0][0]}).fetchall()

        if video_id[0][0] == None:
            add_user_searched_video_sp = 'CALL youtube_schema.add_user_searched_video(:user_id,:video_id)'
            db.session.execute(text(add_user_searched_video_sp), 
                                    {'user_id': user_id[0][0], 'video_id': payload['youtubeVideoInput']})
            db.session.commit()
        else:
            update_user_searched_video_sp = 'CALL youtube_schema.update_user_searched_video(:video_id,:user_id)'
            db.session.execute(text(update_user_searched_video_sp), 
                                    {'video_id': payload['youtubeVideoInput'], 'user_id': user_id[0][0]})
            db.session.commit()

        check_previous_video_analysis_simplified = 'SELECT youtube_schema.check_previous_video_analysis_simplified(:video_id)'
        previous_video_analysis_id = db.session.execute(text(check_previous_video_analysis_simplified), 
                                                            {'video_id': payload['youtubeVideoInput']}).fetchall()
        
        first_initiator = False

        try:
            if previous_video_analysis_id[0][0] == None:
                seed_video_analysis_simplified_sp = 'CALL youtube_schema.seed_video_analysis_simplified(:video_id)'
                db.session.execute(text(seed_video_analysis_simplified_sp), 
                                    {'video_id': payload['youtubeVideoInput']})
                db.session.commit()

                check_previous_video_analysis_simplified = 'SELECT youtube_schema.check_previous_video_analysis_simplified(:video_id)'
                previous_video_analysis_id = db.session.execute(text(check_previous_video_analysis_simplified), 
                                                                {'video_id': payload['youtubeVideoInput']}).fetchall()
                
                add_video_analysis_status_sp = 'CALL youtube_schema.add_video_analysis_status(:previous_video_analysis_id,:status,:user_id)'
                loading_status = 'true'
                db.session.execute(text(add_video_analysis_status_sp), 
                                        {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'status': loading_status, 'user_id': user_id[0][0]})
                db.session.commit()

                first_initiator = True
            else:
                check_video_analysis_loading_status = 'SELECT youtube_schema.check_video_analysis_loading_status(:previous_video_analysis_id)'
                video_analysis_loading_status_id = db.session.execute(text(check_video_analysis_loading_status), {'previous_video_analysis_id': previous_video_analysis_id[0][0]}).fetchall()

                if video_analysis_loading_status_id[0][0] == None:
                    add_video_analysis_status_sp = 'CALL youtube_schema.add_video_analysis_status(:previous_video_analysis_id,:status,:user_id)'
                    loading_status = 'true'
                    db.session.execute(text(add_video_analysis_status_sp), 
                                            {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'status': loading_status, 'user_id': user_id[0][0]})
                    db.session.commit()
                    first_initiator = True

                    check_video_analysis_loading_status = 'SELECT youtube_schema.check_video_analysis_loading_status(:previous_video_analysis_id)'
                    video_analysis_loading_status_id = db.session.execute(text(check_video_analysis_loading_status), {'previous_video_analysis_id': previous_video_analysis_id[0][0]}).fetchall()

                get_video_analysis_loading_status = 'SELECT youtube_schema.get_video_analysis_loading_status(:previous_video_analysis_id)'
                video_analysis_loading_status = db.session.execute(text(get_video_analysis_loading_status), {'previous_video_analysis_id': previous_video_analysis_id[0][0]}).fetchall()

                if video_analysis_loading_status[0][0] != None and first_initiator == False:
                    if video_analysis_loading_status[0][0] == 'true':
                        operation_response = {
                            "operation_success": False,
                            "responsePayload": {
                            },
                            "error_message": ""
                        }
                        response = make_response(json.dumps(operation_response))
                        return response
                    else:
                        check_latest_video_analysis_date = 'SELECT youtube_schema.check_latest_video_analysis_date(:previous_video_analysis_id)'
                        latest_video_analysis_date = db.session.execute(text(check_latest_video_analysis_date), {'previous_video_analysis_id': previous_video_analysis_id[0][0]}).fetchall()

                        latest_date = datetime.strptime(latest_video_analysis_date[0][0], '%Y-%m-%d').date()
                        today = date.today()
                        #date_last_week = today - timedelta(days=7)

                        time_elapsed = today - latest_date

                        if time_elapsed.days < 7:
                            operation_response = {
                                "operation_success": False,
                                "responsePayload": {
                                },
                                "error_message": "not_enough_time_elapsed"
                            }
                            response = make_response(json.dumps(operation_response))
                            return response
                        else:
                            update_video_analysis_status_sp = 'CALL youtube_schema.update_video_analysis_status(:previous_video_analysis_id,:status,:user_id)'
                            loading_status = 'true'
                            db.session.execute(text(update_video_analysis_status_sp), 
                                                    {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'status': loading_status, 'user_id': user_id[0][0]})
                            db.session.commit()

                            first_initiator = True
        except Exception as e:
            if first_initiator:
                update_video_analysis_status_sp = 'CALL youtube_schema.update_video_analysis_status(:previous_video_analysis_id,:status,:user_id)'
                loading_status = 'false'
                db.session.execute(text(update_video_analysis_status_sp), 
                                        {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'status': loading_status, 'user_id': user_id[0][0]})
                db.session.commit()

            operation_response = {
                "operation_success": False,
                "responsePayload": {
                },
                "error_message": ""
            }
            response = make_response(json.dumps(operation_response))
            return response

        """
        channel = youtube_object.channels().list(
            id = payload['channelInput'],
            part = 'contentDetails',
            maxResults = 10
        ).execute()
        """

        video_details = youtube_object.videos().list(
            id = payload['youtubeVideoInput'],
            part = 'snippet',
            maxResults = 10
        ).execute()

        video_title = video_details['items'][0]['snippet']['title']
        published_date = video_details['items'][0]['snippet']['publishedAt']
        publisher = video_details['items'][0]['snippet']['channelTitle']
        video_link = 'https://www.youtube.com/embed/' + payload['youtubeVideoInput']
        if 'maxres' in video_details['items'][0]['snippet']['thumbnails'].keys():
            thumbnail = video_details['items'][0]['snippet']['thumbnails']['maxres']['url']
        elif 'high' in video_details['items'][0]['snippet']['thumbnails'].keys():
            thumbnail = video_details['items'][0]['snippet']['thumbnails']['high']['url']
        elif 'standard' in video_details['items'][0]['snippet']['thumbnails'].keys():
            thumbnail = video_details['items'][0]['snippet']['thumbnails']['standard']['url']
        elif 'medium' in video_details['items'][0]['snippet']['thumbnails'].keys():
            thumbnail = video_details['items'][0]['snippet']['thumbnails']['medium']['url']
        elif 'default' in video_details['items'][0]['snippet']['thumbnails'].keys():
            thumbnail = video_details['items'][0]['snippet']['thumbnails']['default']['url']
        
        url = "https://yt-api.p.rapidapi.com/comments"

        querystring = {"id":payload['youtubeVideoInput'], "sort_by": "newest"}

        headers = {
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": "yt-api.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)
        content_raw = response.content.decode("utf-8")
        content_json = json.loads(content_raw)

        """
        url = "https://youtube-v31.p.rapidapi.com/commentThreads"

        querystring = {"part": "snippet",
                       "videoId": payload['youtubeVideoInput'],
                       "maxResults": content_json_video_details['items'][0]['statistics']['commentCount']
                       }

        response = requests.get(url, headers=headers, params=querystring)

        content_raw = response.content.decode("utf-8")
        content_json = json.loads(content_raw)
        """

        if 'error' in content_json.keys():
            operation_response = {
                "operation_success": False,
                "responsePayload": {
                },
                "error_message": "An error occured when fetching video comments"
            }
            response = make_response(json.dumps(operation_response))
            return response
        
        check_latest_video_analysis_date = 'SELECT youtube_schema.check_latest_video_analysis_date(:previous_video_analysis_id)'
        latest_date = db.session.execute(text(check_latest_video_analysis_date), 
                                                            {'previous_video_analysis_id': previous_video_analysis_id[0][0]}).fetchall()
        
        first_latest_date = True
        
        if latest_date[0][0] != None:
            latest_date = datetime.strptime(latest_date[0][0], '%Y-%m-%d').date()
            latest_date = latest_date - timedelta(days=1)
            first_latest_date = False
        else:
            latest_date = '1990-01-01'
            latest_date = datetime.strptime(latest_date, '%Y-%m-%d').date()

        latest_date_stable = copy.deepcopy(latest_date)
        
        continue_comment_acquisition = True
        raw_top_level_comments = []

        raw_top_level_comments, continue_comment_acquisition, latest_date = unpack_youtube_top_level_comments_yt_api(content_json['data'], 
                                                                                                                     raw_top_level_comments, continue_comment_acquisition, latest_date, latest_date_stable)

        pages_already_gotten = 1

        while 'continuation' in content_json.keys() and content_json['continuation'] != '':
            print('Getting to the next pageToken for ' + video_title)
            querystring = {"id":payload['youtubeVideoInput'], "token":content_json['continuation'], "sort_by": "newest"}

            response = requests.get(url, headers=headers, params=querystring)

            content_raw = response.content.decode("utf-8")
            content_json = json.loads(content_raw)
            
            if continue_comment_acquisition == True and pages_already_gotten < 50:
                raw_top_level_comments, continue_comment_acquisition, latest_date = unpack_youtube_top_level_comments_yt_api(content_json['data'], 
                                                                                                                             raw_top_level_comments, continue_comment_acquisition, latest_date, latest_date_stable)
                pages_already_gotten += 1
            else:
                break

        today = date.today()
        latest_comment_today_time_difference = today - latest_date

        if latest_comment_today_time_difference.days >= 7:
            latest_date = today

        print(pages_already_gotten)
        
        if first_latest_date:
            add_latest_video_analysis_date_sp = 'CALL youtube_schema.add_latest_video_analysis_date(:previous_video_analysis_id,:latest_date)'
            db.session.execute(text(add_latest_video_analysis_date_sp), 
                                    {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'latest_date': latest_date.strftime('%Y-%m-%d')})
            db.session.commit()
        else:
            update_latest_video_analysis_date_sp = 'CALL youtube_schema.update_latest_video_analysis_date(:previous_video_analysis_id,:latest_date)'
            db.session.execute(text(update_latest_video_analysis_date_sp), 
                                    {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'latest_date': latest_date.strftime('%Y-%m-%d')})
            db.session.commit()

        emo_breakdown_result_metadata, emo_breakdown_results = emo_mine_from_list_adhoc(raw_top_level_comments, video_title, published_date,
                                                               publisher, video_link, thumbnail, previous_video_analysis_id[0][0], payload['youtubeVideoInput'])
                                                               
        print('Saving video for ' + video_title)
            
        emo_breakdown_result_metadata_json_data = json.dumps(emo_breakdown_result_metadata, indent=4, cls=GenericJsonEncoder)

        update_video_analysis_sp = 'CALL youtube_schema.update_video_analysis(:previous_video_analysis_id,:previous_video_analysis_json)'
        db.session.execute(text(update_video_analysis_sp), 
                                {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'previous_video_analysis_json': emo_breakdown_result_metadata_json_data})
        db.session.commit()

        delete_emo_breakdown_comments_sp = 'CALL youtube_schema.delete_emo_breakdown_comments(:previous_video_analysis_id)'
        db.session.execute(text(delete_emo_breakdown_comments_sp), 
                                    {'previous_video_analysis_id': previous_video_analysis_id[0][0]})
        db.session.commit()

        for emo_breakdown_result in emo_breakdown_results:
            save_comment_emo(previous_video_analysis_id[0][0], emo_breakdown_result)

        if first_initiator:
            update_video_analysis_status_sp = 'CALL youtube_schema.update_video_analysis_status(:previous_video_analysis_id,:status,:user_id)'
            loading_status = 'false'
            db.session.execute(text(update_video_analysis_status_sp), 
                                    {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'status': loading_status, 'user_id': user_id[0][0]})
            db.session.commit()

        operation_response = {
            "operation_success": True,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))
        return response
        
    except Exception as e:
        if first_initiator:
            update_video_analysis_status_sp = 'CALL youtube_schema.update_video_analysis_status(:previous_video_analysis_id,:status,:user_id)'
            loading_status = 'false'
            db.session.execute(text(update_video_analysis_status_sp), 
                                    {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'status': loading_status, 'user_id': user_id[0][0]})
            db.session.commit()
        
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))

        msg = Message()
        msg.subject = 'Error when performing ad hoc analysis of youtube video'
        msg.recipients = ['antoine186@hotmail.com']
        msg.sender = 'noreply@emomachines.xyz'
        msg.body = str(e)

        Thread(target=mail.send(msg)).start()

        return response

def save_comment_emo(previous_video_analysis_id, comment_emo):
    add_comment_emo_sp = 'CALL youtube_schema.add_comment_emo(:previous_video_analysis_id,:comment_emo)'
    db.session.execute(text(add_comment_emo_sp), {'previous_video_analysis_id': previous_video_analysis_id, 
                                                  'comment_emo': json.dumps(comment_emo, indent=4, cls=GenericJsonEncoder)})
    db.session.commit()
    