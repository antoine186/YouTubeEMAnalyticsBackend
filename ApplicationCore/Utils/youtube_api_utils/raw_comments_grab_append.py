from app_start_helper import youtube_object
from Utils.youtube_api_utils.calculate_emo_from_raw_comments_list import calculate_emo_from_raw_comments_list
from Utils.youtube_api_utils.unpack_youtube_top_level_comments import unpack_youtube_top_level_comments
from Utils.emo_utils.emo_mine_from_list import emo_mine_from_list
from sqlalchemy import text
from app_start_helper import db
from Utils.json_encoder import GenericJsonEncoder
import json

def raw_comments_grab_append(playlist_content, username):
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
            
            get_user_id = 'SELECT user_schema.get_user_id(:username)'

            user_id = db.session.execute(text(get_user_id), {'username': username}).fetchall()

            add_channel_analysis_sp = 'CALL youtube_schema.add_channel_analysis(:user_id,:channel_analysis_json)'

            db.session.execute(text(add_channel_analysis_sp), {'user_id': user_id[0][0], 'channel_analysis_json': emo_breakdown_result_metadata_json_data})

            db.session.commit()
    except Exception as e:
        print(e)
