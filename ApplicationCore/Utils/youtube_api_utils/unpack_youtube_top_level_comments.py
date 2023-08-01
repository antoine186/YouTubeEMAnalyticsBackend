
def unpack_youtube_top_level_comments(video_response_items, raw_comments_list):
    for item in video_response_items:
        raw_comments_list.append(item['snippet']['topLevelComment']['snippet']['textOriginal'])

    return raw_comments_list
