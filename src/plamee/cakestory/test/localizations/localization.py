# -*- coding: utf-8 -*-
from plamee.cakestory import *
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

def get_locale_file(locale):

    my_rows = []
    gd_locales = {}
    wks_index = [0,1,2,3,4,5,7,8 ]

    # connect to google
    json_key = json.load(open("/Users/golovanton/Documents/m3highload-test/localization.json"))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    my_spreadsheet = gc.open_by_url("https://docs.google.com/a/plamee.com/spreadsheets/d/1xpI6bpkUBfACblmUOgXw9l10ePiZ71zOWeJgvdDf5YA/edit?usp=sharing")

    #get worksheet name

    # get locales from file
    for wks_in in wks_index:
        my_rows.extend(my_spreadsheet.get_worksheet(wks_in).get_all_records())

    for row in my_rows:
        gd_locales[row['tag']] = row['text_'+locale]

    return gd_locales

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











