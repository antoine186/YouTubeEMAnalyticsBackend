
def calculate_emo_from_raw_comments_list(raw_comments_list, nn):
    raw_emo_breakdown_list = []

    for comment in raw_comments_list:
        raw_emo_breakdown = nn(comment)
        raw_emo_breakdown_list.append(raw_emo_breakdown)

    return raw_emo_breakdown_list
