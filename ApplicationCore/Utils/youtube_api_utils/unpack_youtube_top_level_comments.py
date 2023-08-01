import re

def unpack_youtube_top_level_comments(video_response_items, raw_comments_list):
    for item in video_response_items:
        comment_string = item['snippet']['topLevelComment']['snippet']['textOriginal']
        comment_string = re.sub('[^A-z0-9 -]', '', comment_string).replace(" ", " ")

        raw_comments_list.append(comment_string)

    return raw_comments_list
