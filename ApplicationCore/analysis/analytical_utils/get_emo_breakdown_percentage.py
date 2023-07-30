from analytical_classes.emo_breakdown_percentage import EmoBreakdownPercentage

def get_emo_breakdown_percentage(emo_breakdown, result_counter, most_emo_dict):
    # This chain of if-else is very bad. It is a compromise.
    for emo in emo_breakdown:
        if emo['label'] == 'anger':
            anger_percentage = emo['score']
        elif emo['label'] == 'disgust':
            disgust_percentage = emo['score']
        elif emo['label'] == 'joy':
            joy_percentage = emo['score']
        elif emo['label'] == 'sadness':
            sadness_percentage = emo['score']
        elif emo['label'] == 'fear':
            fear_percentage = emo['score']
        elif emo['label'] == 'surprise':
            surprise_percentage = emo['score']
        elif emo['label'] == 'neutral':
            neutral_percentage = emo['score']

        if most_emo_dict[emo['label']]['score'] < emo['score']:
            most_emo_dict[emo['label']]['score'] = emo['score']
            most_emo_dict[emo['label']]['index'] = result_counter

    emo_breakdown_percentage = EmoBreakdownPercentage(sadness_percentage, joy_percentage, disgust_percentage, anger_percentage,
                                                        fear_percentage, surprise_percentage, neutral_percentage)
    
    return emo_breakdown_percentage, most_emo_dict

def get_emo_breakdown_percentage_simple_result(emo_breakdown):
    # This chain of if-else is very bad. It is a compromise.
    for emo in emo_breakdown:
        if emo['label'] == 'anger':
            anger_percentage = emo['score']
        elif emo['label'] == 'disgust':
            disgust_percentage = emo['score']
        elif emo['label'] == 'joy':
            joy_percentage = emo['score']
        elif emo['label'] == 'sadness':
            sadness_percentage = emo['score']
        elif emo['label'] == 'fear':
            fear_percentage = emo['score']
        elif emo['label'] == 'surprise':
            surprise_percentage = emo['score']
        elif emo['label'] == 'neutral':
            neutral_percentage = emo['score']

    emo_breakdown_percentage = EmoBreakdownPercentage(sadness_percentage, joy_percentage, disgust_percentage, anger_percentage,
                                                        fear_percentage, surprise_percentage, neutral_percentage)
    
    return emo_breakdown_percentage
