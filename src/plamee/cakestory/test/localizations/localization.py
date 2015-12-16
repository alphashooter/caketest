# -*- coding: utf-8 -*-
from plamee.cakestory import *
from plamee.utils.plameegoogle import get_locale_file

def compare_dict(dict1, dict2):
    result = {}
    if len(dict1) == len(dict2): # inspect len
        if dict1.keys() == dict2.keys(): # inspect keys
            keys_1 = dict1.keys()
            # inspect items
            for key in keys_1:
                if dict1[key] != dict2[key]:
                    result[key] = dict1[key]
            return result
        return "Dictionaries of different tags"
    else:
        return "Dictionaries of different lengths"
# get locales by server

my_client = Client()
locales = my_client.defs.locale_names


# check for bugs

for locale in locales:
    server_locale = my_client.get_locale(locale)
    file_locale = get_locale_file(locale)
    result = compare_dict(server_locale, file_locale)
    if result is not None:
        raise RuntimeError(result)











