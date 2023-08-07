import re
from datetime import datetime, timedelta
from sqlalchemy import text
from app_start_helper import db

def unpack_youtube_top_level_comments_yt_api(video_response_items, raw_comments_list, previous_video_analysis_id, continue_comment_acquisition):
    check_latest_video_analysis_date = 'SELECT youtube_schema.check_latest_video_analysis_date(:previous_video_analysis_id)'
    latest_date = db.session.execute(text(check_latest_video_analysis_date), 
                                                        {'previous_video_analysis_id': previous_video_analysis_id}).fetchall()

    if latest_date[0][0] == None:
        current_latest_date = '1990-01-01'
        current_latest_date = datetime.strptime(current_latest_date, '%Y-%m-%d').date()
    else:
        latest_date = latest_date - timedelta(days=1)
        current_latest_date = latest_date

    for item in video_response_items:
        comment_string = item['textDisplay']
        comment_string = re.sub('[^A-z0-9 -]', '', comment_string).replace(" ", " ")

        current_item_date = datetime.strptime(item['publishDate'], '%Y-%m-%d').date()

        if latest_date[0][0] == None:
            if current_item_date < latest_date:
                continue_comment_acquisition = False
                break

        if current_item_date > current_latest_date:
            current_latest_date = current_item_date
            
        raw_comments_list.append(comment_string)

    if latest_date[0][0] == None and continue_comment_acquisition == True:
        add_latest_video_analysis_date_sp = 'CALL youtube_schema.add_latest_video_analysis_date(:previous_video_analysis_id,:latest_date)'
        db.session.execute(text(add_latest_video_analysis_date_sp), 
                                {'previous_video_analysis_id': previous_video_analysis_id, 'latest_date': current_latest_date.strftime('%Y-%m-%d')})
        db.session.commit()

    return raw_comments_list, continue_comment_acquisition
