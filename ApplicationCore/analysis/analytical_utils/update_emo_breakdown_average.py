
def update_emo_breakdown_average(emo_breakdown_percentage, emo_breakdown_average, sample_count):
    emo_breakdown_average.sadness_percentage = update_weighted_average(
        emo_breakdown_average.sadness_percentage, emo_breakdown_percentage.sadness_percentage, sample_count)
    emo_breakdown_average.joy_percentage = update_weighted_average(
        emo_breakdown_average.joy_percentage, emo_breakdown_percentage.joy_percentage, sample_count)
    emo_breakdown_average.disgust_percentage = update_weighted_average(
        emo_breakdown_average.disgust_percentage, emo_breakdown_percentage.disgust_percentage, sample_count)
    emo_breakdown_average.anger_percentage = update_weighted_average(
        emo_breakdown_average.anger_percentage, emo_breakdown_percentage.anger_percentage, sample_count)
    emo_breakdown_average.fear_percentage = update_weighted_average(
        emo_breakdown_average.fear_percentage, emo_breakdown_percentage.fear_percentage, sample_count)
    emo_breakdown_average.surprise_percentage = update_weighted_average(
        emo_breakdown_average.surprise_percentage, emo_breakdown_percentage.surprise_percentage, sample_count)
    emo_breakdown_average.neutral_percentage = update_weighted_average(
        emo_breakdown_average.neutral_percentage, emo_breakdown_percentage.neutral_percentage, sample_count)

    return emo_breakdown_average

def update_weighted_average(average_percentage, new_percentage, sample_count):
    new_sample_count = sample_count + 1
    new_average_percentage = average_percentage * \
        (sample_count/new_sample_count) + \
        new_percentage * (1 / new_sample_count)

    return new_average_percentage
