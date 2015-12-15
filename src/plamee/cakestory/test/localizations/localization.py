# -*- coding: utf-8 -*-
from plamee.cakestory import *
import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials

def get_locale_file(locale):

    my_rows = []
    gd_locales = {}
    wks_index = [0,1,2,3,4,5,7]

    # connect to google
    json_key = json.load(open("localization.json"))
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

# get locales by server

my_client = Client()
locales = my_client.defs.locale_names


# chek for bugs

for locale in locales:
    server_locale = my_client.get_locale(locale)
    file_locale = get_locale_file(locale)
    for item in server_locale:










