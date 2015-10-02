import re
import gzip

import urlparse
import urllib
import httplib
import HTMLParser

import plamee.utils as utils
import plamee.utils.html

class _FBLoginFormParser(HTMLParser.HTMLParser):
    @staticmethod
    def parse(input):
        parser = _FBLoginFormParser()
        parser.feed(input)
        return parser.__result

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.__result = {}

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            name  = None
            type  = None
            value = None

            for attr in attrs:
                if attr[0] == "name":
                    name  = attr[1]
                elif attr[0] == "value":
                    value = attr[1]
                elif attr[0] == "type":
                    type  = attr[1]

            if name is None:
                return
            if value is None:
                return
            if type is not None and type != "hidden":
                return

            self.__result[name] = value


class FacebookContext(object):

    FACEBOOK_HOST = "www.facebook.com"
    FACEBOOK_LOGIN_URL = "/login.php"

    def __init__(self, user, password):
        self.referer = None
        self.cookies = []
        self.logged  = False

        self.user = user
        self.password = password

    def set_cookie(self, name, value):
        # Check if cookie exists
        for i in range(len(self.cookies)):
            cookie = self.cookies[i]
            if cookie[0] == str(name):
                # Update cookie and return
                if value is None or value == "deleted":
                    self.cookies = self.cookies[:i] + self.cookies[i+1:]
                else:
                    self.cookies[i] = (str(name), str(value))
                return

        # Add cookie
        if value is not None and value != "deleted":
            self.cookies.append( (str(name), str(value)) )

    def create_request(self, host=None, url=None, data=None, follow_redirects=False):
        # Check if user is not logged in
        if not self.logged:
            self.login()

        # Resolve target host
        if host is None:
            host = FacebookContext.FACEBOOK_HOST

        # Create request
        return FacebookRequest(self, host, url, data, follow_redirects)

    def request(self, host=None, url=None, data=None, follow_redirects=False):
        return self.create_request(host, url, data, follow_redirects).evaluate()

    def login(self):
        # Get login form
        response = FacebookRequest(self, FacebookContext.FACEBOOK_HOST, FacebookContext.FACEBOOK_LOGIN_URL).evaluate()

        # Find JS cookies
        js_datr = re.search("\"_js_datr\",\\s*\"(.*?)\"",        response.response)
        js_gate = re.search("\"_js_reg_fb_gate\",\\s*\"(.*?)\"", response.response)
        js_ref  = re.search("\"_js_reg_fb_ref\",\\s*\"(.*?)\"",  response.response)

        if js_datr is not None:
            self.set_cookie("_js_datr", js_datr.group(1))
        if js_gate is not None:
            self.set_cookie("_js_reg_fb_gate", js_gate.group(1))
        if js_ref is not None:
            self.set_cookie("_js_reg_fb_ref", js_ref.group(1))

        # Parse login form
        form = utils.html.get_tag(response, "form", {"id": "login_form"})
        data = _FBLoginFormParser.parse(form)
        data["email"] = self.user
        data["pass"]  = self.password

        url = utils.html.get_tag_attr(form, "action")

        # Try to sign in
        response = FacebookRequest(self, FacebookContext.FACEBOOK_HOST, url, data).evaluate()

        # If redirect - OK
        if response.status == 302:
            self.logged = True
        else:
            raise RuntimeError("Facebook sign-in failed.")


class FacebookRequest:

    def __init__(self, context, host, url = None, data = None, follow_redirects = False):
        self.context = context

        self.host   = host
        self.url    = url
        self.data   = data

        self.follow_redirects = follow_redirects

    def evaluate(self):
        # Resolve URL
        url = "/" if self.url is None else self.url

        # Form default headers
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Host": self.host,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:40.0) Gecko/20100101 Firefox/40.0"
        }

        # Set request referer
        if self.context.referer is not None:
            headers["Referer"] = self.context.referer

        # Set request content
        data = None
        if self.data is not None:
            if isinstance(self.data, dict):
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                data = urllib.urlencode(self.data)
            else:
                headers["Content-Type"] = "application/octet-stream"
                data = self.data

        # Set request cookies
        if self.context.cookies is not None:
            cookies = []
            for cookie in self.context.cookies:
                tmp = {}
                tmp[cookie[0]] = cookie[1]
                cookies.append(urllib.urlencode(tmp))
            if len(cookies) > 0:
                headers["Cookie"] = "; ".join(cookies)

        # Request login
        connection = httplib.HTTPSConnection(host=self.host)
        connection.request(
            "GET" if self.data is None else "POST",
            url,
            data,
            headers
        )
        response = connection.getresponse()

        # Parse result
        result = FacebookResponse(self.host, url, response.status, response.read(), response.msg.headers)

        # Update cookies
        for header in result.headers:
            if header[0] == "set-cookie":
                # Doesn't matter what is a cookie's lifetime and etc., just retrieve its value
                cookie = header[1]
                cookie = cookie.split(";", 1)
                cookie = cookie[0].split("=")
                self.context.set_cookie(cookie[0].strip(), cookie[1].strip())

        # Check response status
        if response.status != 200:
            # Redirect
            if response.status == 302:
                if self.follow_redirects:
                    # Update referer
                    self.context.referer = "https://" + self.host + url
                    # Follow the redirect location
                    location = urlparse.urlparse(response.getheader("Location"))
                    return FacebookRequest(self.context, self.host if location[1] == "" else location[1], location[2], self.data, True).evaluate()
            # Possibly, some error occurred
            else:
                raise RuntimeError("Invalid server response status %d: %s" % (response.status, response.reason))

        # Update referer
        self.context.referer = "https://" + self.host + url

        # Return result
        return result

class FacebookResponse:
    def __init__(self, host, url, status, response, headers):
        self.host     = host
        self.url      = url
        self.status   = status
        self.response = response
        self.headers  = []

        # Parse headers
        for header in headers:
            header = header.split(":", 1)
            self.headers.append( (header[0].lower(), urllib.unquote(header[1].strip())) )

        # Check response content type
        for header in self.headers:
            if header[0] == "content-encoding":
                # Unzip response data
                if header[1] == "gzip":
                    # ~magic~
                    tmp_gz = open("/tmp/fbresptmp", "wb")
                    tmp_gz.write(response)
                    tmp_gz = gzip.open("/tmp/fbresptmp", "rb")
                    self.response = tmp_gz.read()
                    break

    def __str__(self):
        return self.response