import re
from datetime import datetime, timedelta
from sqlalchemy import text
from app_start_helper import db
import copy
from flask import Blueprint, request, make_response

def unpack_youtube_top_level_comments_yt_api(video_response_items, raw_comments_list, continue_comment_acquisition, latest_date_evolvable, latest_date_stable):
    try:
        for item in video_response_items:
            comment_string = item['textDisplay']
            comment_string = re.sub('[^A-z0-9 -]', '', comment_string).replace(" ", " ")

            current_item_date = datetime.strptime(item['publishDate'], '%Y-%m-%d').date()

            if current_item_date.year != 1969:
                if current_item_date < latest_date_stable:
                    continue_comment_acquisition = False
                    break

            if current_item_date > latest_date_evolvable:
                latest_date_evolvable = current_item_date
                
            raw_comments_list.append(comment_string)

        return raw_comments_list, continue_comment_acquisition, latest_date_evolvable
    
    except Exception as e:
        operation_response = {
            "operation_success": False,
            "responsePayload": {
            },
            "error_message": ""
        }
        response = make_response(json.dumps(operation_response))

        return response