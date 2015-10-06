import plamee.utils as utils
import plamee.utils.html

from plamee.fb.facebook import *

class OpenGraphDebugger(object):

    FACEBOOK_DEBUGGER_HOST = "developers.facebook.com"
    FACEBOOK_DEBUGGER_URL  = "/tools/debug/og/object/"

    def __init__(self, user, password):
        self.__dtsg  = None
        self.__url   = None
        self.context = FacebookContext(user, password)

    def check_url(self, url):
        # Form request
        request = self.__get_request(url)

        # Parse response
        response = request.evaluate()

        # Find target route
        form = utils.html.get_tag(response, "form")
        self.__url = utils.html.get_tag_attr(form, "action")

        # Find FB data signature
        form = utils.html.get_tag(form, "input", {"name": "fb_dtsg"})
        self.__dtsg = utils.html.get_tag_attr(form, "value")

        return OpenGraphDebugger.__parse_response(str(response))

    def __get_request(self, url):
        request  = self.context.create_request(OpenGraphDebugger.FACEBOOK_DEBUGGER_HOST, OpenGraphDebugger.FACEBOOK_DEBUGGER_URL + "?" + urllib.urlencode({"q": url}), None)
        return request

    @staticmethod
    def __parse_response(response):
        response = utils.html.remove_tags(response, "head")
        response = utils.html.remove_tags(response, "script")
        response = utils.html.remove_tags(response, "code")

        tables = utils.html.get_tags(response, "table")

        if len(tables) < 4:
            return {
                "status": {"response-code", 404},
                "tags": {},
                "contents": {}
            }

        for i in range(len(tables)):
            tables[i] = utils.html.remove_tags(tables[i], "span", None, True)
            tables[i] = OpenGraphDebugger.__parse_table(tables[i])

        return {
            "status":   OpenGraphDebugger.__parse_status_fields(tables[0]),
            "tags":     OpenGraphDebugger.__parse_tag_fields(tables[1]),
            "contents": OpenGraphDebugger.__parse_content_fields(tables[2])
        }

    @staticmethod
    def __parse_table(table):
        result = utils.html.get_tags(table, "tr")
        for i in range(len(result)):
            result[i] = utils.html.get_tags(result[i], "td")
            for j in range(len(result[i])):
                result[i][j] = utils.html.get_tag_data(result[i][j])
        return result

    @staticmethod
    def __parse_status_fields(table):
        out = {}
        for row in table:
            key = row[0].strip().lower()
            if key == "time scraped":
                out["time-scraped"] = utils.html.get_tag_attr(utils.html.get_tag(row[1], "abbr"), "title")
            elif key == "response code":
                match = re.search("\d+", row[1])
                if match is None:
                    raise RuntimeError("The Scrawler's response code format is not supported.")
                out["response-code"] = int(match.group(0))
            elif key == "fetched url":
                out["fetched-url"] = utils.html.get_tag_attr(utils.html.get_tag(row[1], "a"), "href")
            elif key == "canonical url":
                out["canonical-url"] = utils.html.get_tag_attr(utils.html.get_tag(row[1], "a"), "href")
            elif key == "server ip":
                out["server-ip"] = row[1].strip()
        return out

    @staticmethod
    def __parse_tag_fields(table):
        out = {}
        for row in table:
            key = row[0].strip().lower()
            if key == "meta tag":
                tag = utils.html.unescape(row[1])
                property = utils.html.get_tag_attr(tag, "property")
                content  = utils.html.get_tag_attr(tag, "content")
                if out.has_key(property):
                    if not isinstance(out[property], list):
                        out[property] = [out[property]]
                    out[property].append(content)
                else:
                    out[property] = content
        return out

    @staticmethod
    def __parse_content_fields(table):
        out = {}
        for row in table:
            key = row[0].strip().lower()
            out[key] = row[1]
        return out