from math import floor

def text_divider(article_text, max_characters_allowed):
    nb_tranches = floor(len(article_text) / max_characters_allowed)
    slit_bottom_index = 0
    tranches_list = []

    if (len(article_text) % max_characters_allowed) != 0:
        nb_tranches += 1

    for i in range(1, nb_tranches - 1):
        slit_ceiling_index = max_characters_allowed * i
        tranches_list.append(article_text[slit_bottom_index:slit_ceiling_index])
        slit_bottom_index = slit_ceiling_index

    tranches_list.append(article_text[slit_bottom_index:-1])

    return tranches_list
