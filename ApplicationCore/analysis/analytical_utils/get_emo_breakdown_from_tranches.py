from analysis.analytical_utils.get_emo_breakdown_percentage import get_emo_breakdown_percentage_simple_result
from analysis.analytical_utils.update_emo_breakdown_average import update_emo_breakdown_average
from analytical_classes.emo_breakdown_result import EmoBreakdownResult
from keybert import KeyBERT

def get_emo_breakdown_from_tranches(result_counter, most_emo_dict, tranches_list, main_emo_classification_nn_model, article, result, keyword_extractor_nn):
    tranch_counter = 0

    extracted_keywords_list = []

    for tranch in tranches_list:
        raw_emo_breakdown = main_emo_classification_nn_model(
            tranch)
        emo_breakdown = raw_emo_breakdown[0]
        try:
            raw_extracted_keywords = keyword_extractor_nn.nn_model.extract_keywords(tranch, keyphrase_ngram_range=(1, 2), stop_words=None)
        except:
            keyword_extractor_nn = KeyBERT()
            raw_extracted_keywords = keyword_extractor_nn.extract_keywords(article, keyphrase_ngram_range=(1, 2), stop_words=None)
        extracted_keywords_list.extend(raw_extracted_keywords)

        emo_breakdown_percentage = get_emo_breakdown_percentage_simple_result(emo_breakdown)

        tranch_counter += 1

        if tranch_counter == 1:
            emo_breakdown_average = emo_breakdown_percentage
            continue

        emo_breakdown_average = update_emo_breakdown_average(emo_breakdown_percentage, emo_breakdown_average, tranch_counter - 1)

    if most_emo_dict['anger']['score'] < emo_breakdown_average.anger_percentage:
        most_emo_dict['anger']['score'] = emo_breakdown_average.anger_percentage
        most_emo_dict['anger']['index'] = result_counter

    if most_emo_dict['disgust']['score'] < emo_breakdown_average.disgust_percentage:
        most_emo_dict['disgust']['score'] = emo_breakdown_average.disgust_percentage
        most_emo_dict['disgust']['index'] = result_counter

    if most_emo_dict['joy']['score'] < emo_breakdown_average.joy_percentage:
        most_emo_dict['joy']['score'] = emo_breakdown_average.joy_percentage
        most_emo_dict['joy']['index'] = result_counter

    if most_emo_dict['sadness']['score'] < emo_breakdown_average.sadness_percentage:
        most_emo_dict['sadness']['score'] = emo_breakdown_average.sadness_percentage
        most_emo_dict['sadness']['index'] = result_counter

    if most_emo_dict['fear']['score'] < emo_breakdown_average.fear_percentage:
        most_emo_dict['fear']['score'] = emo_breakdown_average.fear_percentage
        most_emo_dict['fear']['index'] = result_counter

    if most_emo_dict['surprise']['score'] < emo_breakdown_average.surprise_percentage:
        most_emo_dict['surprise']['score'] = emo_breakdown_average.surprise_percentage
        most_emo_dict['surprise']['index'] = result_counter

    if most_emo_dict['neutral']['score'] < emo_breakdown_average.neutral_percentage:
        most_emo_dict['neutral']['score'] = emo_breakdown_average.neutral_percentage
        most_emo_dict['neutral']['index'] = result_counter

    emo_breakdown_result = EmoBreakdownResult(
        article.title, result['description'], result['publisher']['title'], result['published date'], article.canonical_link, emo_breakdown_average, extracted_keywords_list, '')
    
    return emo_breakdown_result, most_emo_dict
