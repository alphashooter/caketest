import re
import HTMLParser

class _GetTagParser(HTMLParser.HTMLParser):
    @staticmethod
    def __check_field(field, value, attrs):
        for attr in attrs:
            if attr[0] == field and re.match(value, attr[1]):
                return True
        return False


    def __init__(self, tag, fields=None):
        self.__tag = tag
        self.__fld = fields
        self.__txt = ""
        self.__sps = None
        self.__eps = None
        self.__off = None
        self.__cnt = -1

        HTMLParser.HTMLParser.__init__(self)

    def feed(self, data):
        self.__txt += data
        HTMLParser.HTMLParser.feed(self, data)

    def reset(self):
        self.__txt = ""
        HTMLParser.HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        if self.__cnt < 0:
            if tag == self.__tag:
                if self.__fld is None:
                    self.__cnt = 1
                    self.__sps = self.getpos()
                else:
                    for field in self.__fld:
                        if not _GetTagParser.__check_field(field, self.__fld[field], attrs):
                            return
                    self.__cnt = 1
                    self.__sps = self.getpos()
        elif self.__cnt == 0:
            self.__eps = self.getpos()
            self.__cnt = -1
        else:
            if tag == self.__tag:
                self.__cnt = self.__cnt + 1

    def handle_endtag(self, tag):
        if self.__cnt > 0:
            if tag == self.__tag:
                self.__cnt = self.__cnt - 1
        elif self.__cnt == 0:
            self.__eps = self.getpos()
            self.__cnt = -1

    def get_result(self):
        if self.__sps is None:
            return ""

        start_pos = 0
        end_pos   = 0

        lines = self.__txt.splitlines(True)

        if self.__eps is None:
            self.__eps = (0, 0)
            self.__eps[0] = len(lines)
            self.__eps[1] = len(lines[self.__eps[0] - 1])

        for i in range(0, self.__sps[0] - 1):
            start_pos += len(lines[i])
            end_pos   += len(lines[i])
        for i in range(self.__sps[0] - 1, self.__eps[0] - 1):
            end_pos   += len(lines[i])

        start_pos += self.__sps[1]
        end_pos   += self.__eps[1]

        return self.__txt[start_pos:end_pos]


class _GetTagAttrParser(HTMLParser.HTMLParser):
    def __init__(self, field):
        self.__fld = field
        self.__rlt = ""
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == self.__fld:
                self.__rlt = attr[1]

    def get_result(self):
        return self.__rlt


######


def get_tag(input, tag, fields=None):
    parser = _GetTagParser(tag, fields)
    parser.feed(str(input))
    return parser.get_result()


def get_tag_attr(input, field):
    parser = _GetTagAttrParser(field)
    parser.feed(str(input))
    return parser.get_result()