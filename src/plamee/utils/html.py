import re
import string
import HTMLParser

class _TagInfo:
    def __init__(self, pos):
        self.startpos = pos
        self.endpos   = None

        self.data_startpos = None
        self.data_endpos   = None

        self.counter  = 0

class _GetTagsParser(HTMLParser.HTMLParser):
    @staticmethod
    def __check_field(field, value, attrs):
        for attr in attrs:
            if attr[0] == field and re.match(value, attr[1]):
                return True
        return False


    def __init__(self, tag, fields=None):
        self.__tag     = tag
        self.__fields  = fields
        self.__input   = ""
        self.__pending = []
        self.__result  = []

        HTMLParser.HTMLParser.__init__(self)

    def feed(self, data):
        self.__input += data
        HTMLParser.HTMLParser.feed(self, data)

    def reset(self):
        self.__input = ""
        HTMLParser.HTMLParser.reset(self)

    def handle_starttag(self, tag, attrs):
        for pending_tag in self.__pending:
            if pending_tag.counter == 0:
                pending_tag.endpos = self.getpos()
                self.__result.append(pending_tag)
                self.__pending.remove(pending_tag)
            elif pending_tag.counter == 1 and pending_tag.data_startpos is None:
                pending_tag.data_startpos = self.getpos()

        if tag is None or tag == self.__tag:
            if self.__fields is None:
                self.__pending.append(_TagInfo(self.getpos()))
            else:
                is_target_tag = True

                for field in self.__fields:
                    is_target_tag = is_target_tag and _GetTagsParser.__check_field(field, self.__fields[field], attrs)
                    if not is_target_tag:
                        break

                if is_target_tag:
                    self.__pending.append(_TagInfo(self.getpos()))

            for pending_tag in self.__pending:
                pending_tag.counter += 1

    def handle_data(self, data):
        for pending_tag in self.__pending:
            if pending_tag.counter == 1 and pending_tag.data_startpos is None:
                pending_tag.data_startpos = self.getpos()

    def handle_endtag(self, tag):
        for pending_tag in self.__pending:
            if pending_tag.counter == 0:
                pending_tag.endpos = self.getpos()
                self.__result.append(pending_tag)
                self.__pending.remove(pending_tag)

        if tag is None or tag == self.__tag:
            for pending_tag in self.__pending:
                pending_tag.counter -= 1
                if pending_tag.counter == 0:
                    pending_tag.data_endpos = self.getpos()

    def handle_entityref(self, name):
        for pending_tag in self.__pending:
            if pending_tag.counter == 1 and pending_tag.data_startpos is None:
                pending_tag.data_startpos = self.getpos()

    def handle_charref(self, name):
        for pending_tag in self.__pending:
            if pending_tag.counter == 1 and pending_tag.data_startpos is None:
                pending_tag.data_startpos = self.getpos()

    def get_input(self):
        return self.__input

    def get_raw_result(self):
        lines = self.__input.splitlines(True)

        pending = self.__pending[:]
        result  = self.__result[:]

        for pending_tag in pending:
            if pending_tag.counter != 0:
                pending.remove(pending_tag)
            else:
                pending_tag.endpos = (len(lines), len(lines[len(lines) - 1]))
                result.append(pending_tag)
                pending.remove(pending_tag)

        return result

    def get_result(self):
        out = []

        lines = self.__input.splitlines(True)

        pending = self.__pending[:]
        result  = self.__result[:]

        for pending_tag in pending:
            if pending_tag.counter != 0:
                pending.remove(pending_tag)
            else:
                pending_tag.endpos = (len(lines), len(lines[len(lines) - 1]))
                result.append(pending_tag)
                pending.remove(pending_tag)

        for result_tag in result:
            start_pos = 0
            end_pos   = 0

            for i in range(0, result_tag.startpos[0] - 1):
                start_pos += len(lines[i])
                end_pos   += len(lines[i])
            for i in range(result_tag.startpos[0] - 1, result_tag.endpos[0] - 1):
                end_pos   += len(lines[i])

            start_pos += result_tag.startpos[1]
            end_pos   += result_tag.endpos[1]

            out.append(self.__input[start_pos:end_pos])

        return out


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


class _GetTagDataParser(HTMLParser.HTMLParser):
    def __init__(self, input):
        self.__input    = input
        self.__is_first = True
        self.__startpos = None
        self.__endpos   = None
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if self.__is_first:
            self.__is_first = False
            return

        if self.__startpos is None:
            self.__startpos = self.getpos()

    def handle_endtag(self, tag):
        self.__endpos = self.getpos()

    def handle_data(self, data):
        if self.__startpos is None:
            if not self.__is_first:
                self.__startpos = self.getpos()

    def handle_entityref(self, name):
        if self.__startpos is None:
            if not self.__is_first:
                self.__startpos = self.getpos()

    def handle_charref(self, name):
        if self.__startpos is None:
            if not self.__is_first:
                self.__startpos = self.getpos()

    def get_result(self):
        if self.__startpos is None:
            return ""

        lines = self.__input.splitlines(True)

        if self.__endpos is None:
            self.__endpos = (len(lines), len(lines[len(lines) - 1]))

        start_pos = 0
        end_pos   = 0

        for i in range(0, self.__startpos[0] - 1):
            start_pos += len(lines[i])
            end_pos   += len(lines[i])
        for i in range(self.__startpos[0] - 1, self.__endpos[0] - 1):
            end_pos   += len(lines[i])

        start_pos += self.__startpos[1]
        end_pos   += self.__endpos[1]

        return self.__input[start_pos:end_pos]


class _IndentParser(HTMLParser.HTMLParser):
    def __init__(self):
        self.__result        = ""
        self.__depth         = 0
        self.__prevent_br    = 0
        self.__ignore_endtag = False
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        text = self.get_starttag_text().strip()
        if text[len(text)-2:] == "/>":
            self.__ignore_endtag = True
            self.__result += str.format(
                "\n{: >%ds}{:s}" % (4 * self.__depth) if self.__prevent_br == 0 else "{:s}{:s}",
                "",
                "<%s %s/>" % (tag, reduce(lambda out, x: out + str("%s=\"%s\" " % (x[0], x[1])), attrs, ""))
            )
        else:
            self.__result += str.format(
                "\n{: >%ds}{:s}" % (4 * self.__depth) if self.__prevent_br == 0 else "{:s}{:s}",
                "",
                "<%s %s>" % (tag, reduce(lambda out, x: out + str("%s=\"%s\"" % (x[0], x[1])), attrs, ""))
            )
            if self.__prevent_br > 0:
                self.__prevent_br += 1
            self.__depth += 1

    def handle_data(self, data):
        if self.__prevent_br == 0 and self.__depth > 0:
            self.__prevent_br = 1
        self.__result += data

    def handle_entityref(self, name):
        if self.__prevent_br == 0 and self.__depth > 0:
            self.__prevent_br = 1
        self.__result += "&%s;" % name

    def handle_charref(self, name):
        if self.__prevent_br == 0 and self.__depth > 0:
            self.__prevent_br = 1
        self.__result += "&#%s;" % name

    def handle_endtag(self, tag):
        if self.__ignore_endtag:
            self.__ignore_endtag = False
            return

        self.__depth -= 1
        self.__result += str.format(
            "\n{: >%ds}{:s}" % (4 * self.__depth) if self.__prevent_br == 0 else "{:s}{:s}",
            "",
            "</%s>" % tag
        )

        if self.__prevent_br > 0:
            self.__prevent_br -= 1

    def get_result(self):
        return self.__result



######


def get_tags(input, tag, fields=None):
    parser = _GetTagsParser(tag, fields)
    parser.feed(str(input))
    return parser.get_result()

def get_tag(input, tag, fields=None, index=0):
    parser = _GetTagsParser(tag, fields)
    parser.feed(str(input))
    result = parser.get_result()

    if len(result) > index:
        return result[index]

    return ""

def get_first_tag(input, tag, fields=None):
    parser = _GetTagsParser(tag, fields)
    parser.feed(str(input))
    result = parser.get_result()

    if len(result) > 0:
        return result[0]

    return ""

def get_last_tag(input, tag, fields=None):
    parser = _GetTagsParser(tag, fields)
    parser.feed(str(input))
    result = parser.get_result()

    if len(result) > 0:
        return result[len(result) - 1]

    return ""

def remove_tags(input, tag=None, fields=None, skip_contents=False):
    if skip_contents:
        out = str(input)[:]

        while True:
            parser = _GetTagsParser(tag, fields)
            parser.feed(out)
            result = parser.get_raw_result()

            lines = out.splitlines(True)

            if not len(result):
                return out

            result_tag = result[0]

            start_pos = 0
            end_pos   = 0

            for i in range(0, result_tag.data_endpos[0] - 1):
                start_pos += len(lines[i])
                end_pos   += len(lines[i])
            for i in range(result_tag.data_endpos[0] - 1, result_tag.endpos[0] - 1):
                end_pos   += len(lines[i])

            start_pos += result_tag.data_endpos[1]
            end_pos   += result_tag.endpos[1]

            if start_pos < len(out):
                if end_pos < len(out):
                    out = out[:start_pos] + out[end_pos:]
                else:
                    out = out[:start_pos]

            start_pos = 0
            end_pos   = 0

            for i in range(0, result_tag.startpos[0] - 1):
                start_pos += len(lines[i])
                end_pos   += len(lines[i])
            for i in range(result_tag.startpos[0] - 1, result_tag.data_startpos[0] - 1):
                end_pos   += len(lines[i])

            start_pos += result_tag.startpos[1]
            end_pos   += result_tag.data_startpos[1]

            if start_pos < len(out):
                if end_pos < len(out):
                    out = out[:start_pos] + out[end_pos:]
                else:
                    out = out[:start_pos]

    else:
        parser = _GetTagsParser(tag, fields)
        parser.feed(str(input))
        result = parser.get_raw_result()

        out   = parser.get_input()
        lines = out.splitlines(True)

        for i in reversed(range(len(result))):
            result_tag = result[i]

            start_pos = 0
            end_pos   = 0

            for i in range(0, result_tag.startpos[0] - 1):
                start_pos += len(lines[i])
                end_pos   += len(lines[i])
            for i in range(result_tag.startpos[0] - 1, result_tag.endpos[0] - 1):
                end_pos   += len(lines[i])

            start_pos += result_tag.startpos[1]
            end_pos   += result_tag.endpos[1]

            if start_pos < len(out):
                if end_pos < len(out):
                    out = out[:start_pos] + out[end_pos:]
                else:
                    out = out[:start_pos]

        return out

def get_tag_data(input):
    parser = _GetTagDataParser(input)
    parser.feed(str(input))
    return parser.get_result()


def get_tag_attr(input, field):
    parser = _GetTagAttrParser(field)
    parser.feed(str(input))
    return parser.get_result()

def reindent(input):
    parser = _IndentParser()
    parser.feed(input)
    return parser.get_result()

def unescape(input):
    result = input[:]

    aliases = {
        "quot": "\"",
        "amp":  "&",
        "gt":   ">",
        "lt":   "<"
    }

    pattern = r"&((?:#\d+)|(?:(?:\w|\d)+));"
    while True:
        match = re.search(pattern, result)
        if match is None:
            break

        value = match.group(1)
        if aliases.has_key(value):
            result = result[:match.start()] + aliases[value] + result[match.end():]
        elif value[0] == "#":
            if value[1].lower() == "x":
                value = unichr(string.atoi(value[2:], 16))
            else:
                value = unichr(string.atoi(value[1:]))
            result = result[:match.start()] + value + result[match.end():]

    return result