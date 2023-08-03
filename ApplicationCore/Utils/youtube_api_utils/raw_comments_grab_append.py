from app_start_helper import youtube_object
from Utils.youtube_api_utils.calculate_emo_from_raw_comments_list import calculate_emo_from_raw_comments_list
from Utils.youtube_api_utils.unpack_youtube_top_level_comments import unpack_youtube_top_level_comments
from Utils.emo_utils.emo_mine_from_list import emo_mine_from_list
from sqlalchemy import text
from app_start_helper import db
from Utils.json_encoder import GenericJsonEncoder
import json
from flask_mail import Mail, Message
from threading import Thread
from app_start_helper import mail

def raw_comments_grab_append(playlist_content, user_id, previous_channel_analysis_id):
    try:
        for item in playlist_content['items']:
            raw_top_level_comments = []
            video_title = item['snippet']['title']
            published_date = item['snippet']['publishedAt']
            publisher = item['snippet']['videoOwnerChannelTitle']
            video_link = 'https://www.youtube.com/embed/' + item['contentDetails']['videoId']
            if 'maxres' in item['snippet']['thumbnails'].keys():
                thumbnail = item['snippet']['thumbnails']['maxres']['url']
            elif 'high' in item['snippet']['thumbnails'].keys():
                thumbnail = item['snippet']['thumbnails']['high']['url']
            elif 'standard' in item['snippet']['thumbnails'].keys():
                thumbnail = item['snippet']['thumbnails']['standard']['url']
            elif 'medium' in item['snippet']['thumbnails'].keys():
                thumbnail = item['snippet']['thumbnails']['medium']['url']
            elif 'default' in item['snippet']['thumbnails'].keys():
                thumbnail = item['snippet']['thumbnails']['default']['url']

            video_response = youtube_object.commentThreads().list(part='id,snippet,replies',
                                                            videoId=item['contentDetails']['videoId']
                                                            ).execute()
            
            check_previous_video_analysis = 'SELECT youtube_schema.check_previous_video_analysis(:_previous_channel_analysis_id,:_video_id)'
            previous_video_analysis_id = db.session.execute(text(check_previous_video_analysis), 
                                                              {'_previous_channel_analysis_id': previous_channel_analysis_id[0][0], '_video_id': item['contentDetails']['videoId']}).fetchall()
            
            if previous_video_analysis_id[0][0] == None:
                seed_video_analysis_sp = 'CALL youtube_schema.seed_video_analysis(:video_id,:previous_channel_analysis_id)'
                db.session.execute(text(seed_video_analysis_sp), 
                                   {'video_id': item['contentDetails']['videoId'], 'previous_channel_analysis_id': previous_channel_analysis_id[0][0]})
                db.session.commit()

                check_previous_video_analysis = 'SELECT youtube_schema.check_previous_video_analysis(:_previous_channel_analysis_id,:_video_id)'
                previous_video_analysis_id = db.session.execute(text(check_previous_video_analysis), 
                            {'_previous_channel_analysis_id': previous_channel_analysis_id[0][0], '_video_id': item['contentDetails']['videoId']}).fetchall()
            
            print('First mining of new video ' + video_title)

            raw_top_level_comments = unpack_youtube_top_level_comments(video_response['items'], raw_top_level_comments)

            while 'nextPageToken' in video_response.keys() and video_response['nextPageToken'] != '':
                print('Getting to the next pageToken for ' + video_title)
                video_response = youtube_object.commentThreads().list(part='id,snippet,replies',
                                                                    videoId=item['contentDetails']['videoId'],
                                                                    pageToken=video_response['nextPageToken']).execute()
                
                raw_top_level_comments = unpack_youtube_top_level_comments(video_response['items'], raw_top_level_comments)
        
            emo_breakdown_result_metadata, emo_breakdown_results = emo_mine_from_list(raw_top_level_comments, video_title, published_date,
                                                               publisher, video_link, thumbnail, previous_video_analysis_id[0][0])
            
            print('Saving video for ' + video_title)
            
            emo_breakdown_result_metadata_json_data = json.dumps(emo_breakdown_result_metadata, indent=4, cls=GenericJsonEncoder)

            update_video_analysis_sp = 'CALL youtube_schema.update_video_analysis(:previous_video_analysis_id,:previous_video_analysis_json)'
            db.session.execute(text(update_video_analysis_sp), 
                                   {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'previous_video_analysis_json': emo_breakdown_result_metadata_json_data})
            db.session.commit()

            check_previous_video_analysis = 'SELECT youtube_schema.check_previous_video_analysis(:_previous_channel_analysis_id,:_video_id)'
            previous_video_analysis_id = db.session.execute(text(check_previous_video_analysis), 
                            {'_previous_channel_analysis_id': previous_channel_analysis_id[0][0], '_video_id': item['contentDetails']['videoId']}).fetchall()

            for emo_breakdown_result in emo_breakdown_results:
                save_comment_emo(previous_video_analysis_id[0][0], emo_breakdown_result)

    except Exception as e:
        print(e)

        msg = Message()
        msg.subject = 'Error when grabbing and mining top level comments for a single video'
        msg.recipients = ['antoine186@hotmail.com']
        msg.sender = 'noreply@emomachines.xyz'
        msg.body = str(e)

        Thread(target=mail.send(msg)).start()

def save_comment_emo(previous_video_analysis_id, comment_emo):
    add_comment_emo_sp = 'CALL youtube_schema.add_comment_emo(:previous_video_analysis_id,:comment_emo)'
    db.session.execute(text(add_comment_emo_sp), {'previous_video_analysis_id': previous_video_analysis_id, 
                                                  'comment_emo': json.dumps(comment_emo, indent=4, cls=GenericJsonEncoder)})
    db.session.commit()

