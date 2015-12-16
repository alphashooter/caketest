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


def put_cases_to_google(filename, key, current_case):
    # Google put in test cases by u-test format

    json_key = json.load(open(key))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    wks = gc.open(filename).sheet1
    i = 10
    for case in current_case:
        wks.update_acell("A" + str(i), case["#"])
        wks.update_acell("B" + str(i), case["Title"])
        wks.update_acell("C" + str(i), case["Section"])
        wks.update_acell("D" + str(i), case["Precondition"])
        wks.update_acell("E" + str(i), case["Steps"])
        wks.update_acell("F" + str(i), case["Result"])
        wks.update_acell("H" + str(i), case["Estimate"])
        i += 1

    return None

def prepare_utest(temp_cases):
    result = []
    int_case = {}
    i = 1
    for temp_case in temp_cases:
        if temp_case["custom_steps_separated"] is not None:
            for item_2 in temp_case["custom_steps_separated"]:
                int_case["#"] = i
                int_case["Title"] = temp_case["title"]
                int_case["Section"] = section_name(temp_case["section_id"])
                int_case["Precondition"] = temp_case["custom_preconds"]
                int_case["Steps"] = item_2["content"]
                int_case["Result"] = item_2["expected"]
                int_case["Estimate"] = temp_case["estimate"]
                result.append(int_case.copy())
                i += 1
                int_case.clear()
        else:
            int_case["#"] = i
            int_case["Title"] = temp_case["title"]
            int_case["Section"] = section_name(temp_case["section_id"])
            int_case["Precondition"] = temp_case["custom_preconds"]
            int_case["Steps"] = temp_case["custom_steps"]
            int_case["Result"] = temp_case["custom_expected"]
            int_case["Estimate"] = temp_case["estimate"]
            result.append(int_case.copy())
            i += 1
            int_case.clear()

    return result