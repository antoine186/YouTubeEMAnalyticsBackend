
def average_merger(emo_breakdown_result_metadata, previous_twitter_result, sample_size, previous_sample_size):
    emo_breakdown_result_metadata.average_emo_breakdown.anger_percentage = ((emo_breakdown_result_metadata.average_emo_breakdown.anger_percentage) * (sample_size / (sample_size + previous_sample_size))) \
        + ((previous_twitter_result['average_emo_breakdown']['anger_percentage']) * (previous_sample_size / (sample_size + previous_sample_size)))
    emo_breakdown_result_metadata.average_emo_breakdown.disgust_percentage = ((emo_breakdown_result_metadata.average_emo_breakdown.disgust_percentage) * (sample_size / (sample_size + previous_sample_size))) \
        + ((previous_twitter_result['average_emo_breakdown']['disgust_percentage']) * (previous_sample_size / (sample_size + previous_sample_size)))
    emo_breakdown_result_metadata.average_emo_breakdown.fear_percentage = ((emo_breakdown_result_metadata.average_emo_breakdown.fear_percentage) * (sample_size / (sample_size + previous_sample_size))) \
        + ((previous_twitter_result['average_emo_breakdown']['fear_percentage']) * (previous_sample_size / (sample_size + previous_sample_size)))
    emo_breakdown_result_metadata.average_emo_breakdown.joy_percentage = ((emo_breakdown_result_metadata.average_emo_breakdown.joy_percentage) * (sample_size / (sample_size + previous_sample_size))) \
        + ((previous_twitter_result['average_emo_breakdown']['joy_percentage']) * (previous_sample_size / (sample_size + previous_sample_size)))
    emo_breakdown_result_metadata.average_emo_breakdown.neutral_percentage = ((emo_breakdown_result_metadata.average_emo_breakdown.neutral_percentage) * (sample_size / (sample_size + previous_sample_size))) \
        + ((previous_twitter_result['average_emo_breakdown']['neutral_percentage']) * (previous_sample_size / (sample_size + previous_sample_size)))
    emo_breakdown_result_metadata.average_emo_breakdown.sadness_percentage = ((emo_breakdown_result_metadata.average_emo_breakdown.sadness_percentage) * (sample_size / (sample_size + previous_sample_size))) \
        + ((previous_twitter_result['average_emo_breakdown']['sadness_percentage']) * (previous_sample_size / (sample_size + previous_sample_size)))
    emo_breakdown_result_metadata.average_emo_breakdown.surprise_percentage = ((emo_breakdown_result_metadata.average_emo_breakdown.surprise_percentage) * (sample_size / (sample_size + previous_sample_size))) \
        + ((previous_twitter_result['average_emo_breakdown']['surprise_percentage']) * (previous_sample_size / (sample_size + previous_sample_size)))
    
    if (emo_breakdown_result_metadata.most_angry_article.emo_breakdown.anger_percentage < previous_twitter_result['most_angry_article']['emo_breakdown']['anger_percentage']):
        emo_breakdown_result_metadata.most_angry_article = previous_twitter_result['most_angry_article']

    if (emo_breakdown_result_metadata.most_disgusted_article.emo_breakdown.disgust_percentage < previous_twitter_result['most_disgusted_article']['emo_breakdown']['disgust_percentage']):
        emo_breakdown_result_metadata.most_disgusted_article = previous_twitter_result['most_disgusted_article']

    if (emo_breakdown_result_metadata.most_fearful_article.emo_breakdown.fear_percentage < previous_twitter_result['most_fearful_article']['emo_breakdown']['fear_percentage']):
        emo_breakdown_result_metadata.most_fearful_article = previous_twitter_result['most_fearful_article']

    if (emo_breakdown_result_metadata.happiest_article.emo_breakdown.joy_percentage < previous_twitter_result['happiest_article']['emo_breakdown']['joy_percentage']):
        emo_breakdown_result_metadata.happiest_article = previous_twitter_result['happiest_article']

    if (emo_breakdown_result_metadata.most_neutral_article.emo_breakdown.neutral_percentage < previous_twitter_result['most_neutral_article']['emo_breakdown']['neutral_percentage']):
        emo_breakdown_result_metadata.most_neutral_article = previous_twitter_result['most_neutral_article']

    if (emo_breakdown_result_metadata.sadest_article.emo_breakdown.sadness_percentage < previous_twitter_result['sadest_article']['emo_breakdown']['sadness_percentage']):
        emo_breakdown_result_metadata.sadest_article = previous_twitter_result['sadest_article']

    if (emo_breakdown_result_metadata.most_surprised_article.emo_breakdown.surprise_percentage < previous_twitter_result['most_surprised_article']['emo_breakdown']['surprise_percentage']):
        emo_breakdown_result_metadata.most_surprised_article = previous_twitter_result['most_surprised_article']

    return emo_breakdown_result_metadata
