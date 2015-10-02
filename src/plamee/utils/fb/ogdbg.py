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
        OpenGraphDebugger.__parse_response(response)

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
        # TODO: Response parsing
        pass