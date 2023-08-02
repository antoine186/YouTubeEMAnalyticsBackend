from math import floor
from Utils.text_divider import text_divider
from app_start_helper import model_max_characters_allowed

def text_divider_by_word_count(article_text, max_words_allowed):
    string_word_list_in_order = article_text.split()
    nb_tranches = floor(len(string_word_list_in_order) / max_words_allowed)
    slit_bottom_index = 0
    tranches_list = []

    if (len(string_word_list_in_order) % max_words_allowed) != 0:
        nb_tranches += 1

    for i in range(1, nb_tranches + 1):
        slit_ceiling_index = max_words_allowed * i
        
        raw_mini_tranch = string_word_list_in_order[slit_bottom_index:-1]

        mini_tranch_string = ''
        for word in raw_mini_tranch:
            mini_tranch_string += word
            mini_tranch_string += ' '

        if len(mini_tranch_string) > 600:
            inner_tranches_list = text_divider(mini_tranch_string, model_max_characters_allowed)
            tranches_list = tranches_list + inner_tranches_list

        print('Length of current mini tranch ' + str(len(mini_tranch_string)))
        tranches_list.append(mini_tranch_string)

        slit_bottom_index = slit_ceiling_index

    return tranches_list
