from math import floor

def list_divide_into_lists(list_to_divide, divisor_size):
    nb_tranches = floor(len(list_to_divide) / divisor_size)
    slit_bottom_index = 0
    tranches_list = []

    if (len(list_to_divide) % divisor_size) != 0:
        nb_tranches += 1

    for i in range(1, nb_tranches - 1):
        slit_ceiling_index = divisor_size * i
        tranches_list.append(list_to_divide[slit_bottom_index:slit_ceiling_index])
        slit_bottom_index = slit_ceiling_index

    tranches_list.append(list_to_divide[slit_bottom_index:slit_bottom_index + divisor_size])

    slit_bottom_index = slit_bottom_index + divisor_size
    tranches_list.append(list_to_divide[slit_bottom_index:-1])

    return tranches_list
