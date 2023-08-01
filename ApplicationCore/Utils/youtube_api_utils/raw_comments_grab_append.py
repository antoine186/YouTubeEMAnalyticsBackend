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
            video_link = 'https://www.youtube.com/watch?v=' + item['contentDetails']['videoId']
            thumbnail = item['snippet']['thumbnails']['maxres']['url']

            video_response = youtube_object.commentThreads().list(part='id,snippet,replies',
                                                            videoId=item['contentDetails']['videoId']
                                                            ).execute()

            raw_top_level_comments = unpack_youtube_top_level_comments(video_response['items'], raw_top_level_comments)

            while 'nextPageToken' in video_response.keys() and video_response['nextPageToken'] != '':
                video_response = youtube_object.commentThreads().list(part='id,snippet,replies',
                                                                    videoId=item['contentDetails']['videoId'],
                                                                    pageToken=video_response['nextPageToken']).execute()
                
                raw_top_level_comments = unpack_youtube_top_level_comments(video_response['items'], raw_top_level_comments)
        
            emo_breakdown_result_metadata = emo_mine_from_list(raw_top_level_comments, video_title, published_date,
                                                               publisher, video_link, thumbnail)
            
            emo_breakdown_result_metadata_json_data = json.dumps(emo_breakdown_result_metadata, indent=4, cls=GenericJsonEncoder)

            check_previous_video_analysis = 'SELECT youtube_schema.check_previous_video_analysis(:_previous_channel_analysis_id,:_video_id)'
            previous_video_analysis_id = db.session.execute(text(check_previous_video_analysis), 
                                                              {'_previous_channel_analysis_id': previous_channel_analysis_id[0][0], '_video_id': item['contentDetails']['videoId']}).fetchall()
            
            if previous_video_analysis_id[0][0] != None:
                update_video_analysis_sp = 'CALL youtube_schema.update_video_analysis(:previous_video_analysis_id,:previous_video_analysis_json)'
                db.session.execute(text(update_video_analysis_sp), {'previous_video_analysis_id': previous_video_analysis_id[0][0], 'previous_video_analysis_json': emo_breakdown_result_metadata_json_data})
                db.session.commit()
            else:
                add_video_analysis_sp = 'CALL youtube_schema.add_video_analysis(:video_id,:previous_channel_analysis_id,:previous_video_analysis_json)'
                db.session.execute(text(add_video_analysis_sp), 
                                   {'video_id': item['contentDetails']['videoId'], 'previous_channel_analysis_id': previous_channel_analysis_id[0][0], 'previous_video_analysis_json': emo_breakdown_result_metadata_json_data})
                db.session.commit()

    except Exception as e:
        print(e)

        msg = Message()
        msg.subject = 'Error when grabbing and mining top level comments for a single video'
        msg.recipients = ['antoine186@hotmail.com']
        msg.sender = 'noreply@emomachines.xyz'
        msg.body = str(e)

        Thread(target=mail.send(msg)).start()
