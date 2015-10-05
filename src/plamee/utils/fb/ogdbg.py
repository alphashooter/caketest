import plamee.utils as utils
import plamee.utils.html

from plamee.utils.fb.facebook import *

class OpenGraphDebugger(object):

    FACEBOOK_DEBUGGER_HOST = "developers.facebook.com"
    FACEBOOK_DEBUGGER_URL  = "/tools/debug/og/object/"

    def __init__(self, user, password):
        self.context = FacebookContext(user, password)

    def check_url(self, url):
        # Form request
        request = self.__get_request()
        request.data["q"]       = url
        request.data["version"] = ""

        # Parse response
        response = request.evaluate()
        return OpenGraphDebugger.__parse_response(str(response))

    def __get_request(self):
        request  = self.context.create_request(OpenGraphDebugger.FACEBOOK_DEBUGGER_HOST, None, None)

        # Get debugger form
        response = self.context.request(OpenGraphDebugger.FACEBOOK_DEBUGGER_HOST, OpenGraphDebugger.FACEBOOK_DEBUGGER_URL)

        # Find target route
        response     = utils.html.get_tag(response, "form")
        request.url  = utils.html.get_tag_attr(response, "action")

        # Find FB data signature
        response     = utils.html.get_tag(response, "input", {"name": "fb_dtsg"})
        request.data = {"fb_dtsg": utils.html.get_tag_attr(response, "value")}

        return request

    @staticmethod
    def __parse_response(response):
        response = utils.html.remove_tags(response, "head")
        response = utils.html.remove_tags(response, "script")
        response = utils.html.remove_tags(response, "code")

        tables = utils.html.get_tags(response, "table")

        for i in range(len(tables)):
            tables[i] = utils.html.remove_tags(tables[i], "span", None, True)
            tables[i] = OpenGraphDebugger.__parse_table(tables[i])

        return {
            "status":   tables[0],
            "tags":     tables[1],
            "contents": tables[2]
        }

    @staticmethod
    def __parse_table(table):
        result = utils.html.get_tags(table, "tr")
        for i in range(len(result)):
            result[i] = utils.html.get_tags(result[i], "td")
            for j in range(len(result[i])):
                result[i][j] = utils.html.get_tag_data(result[i][j])
        return result
