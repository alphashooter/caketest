import re
from plamee import log

class ConfigParser(object):
    def __init__(self, file, pos=0, indent=0):
        self.__file = file
        self.__input = open(file, "r").read()
        self.__pos = pos
        self.__line = pos
        self.__linenum = 1
        self.__indent = indent
        self.__initial = True

    def test(self, pattern):
        pos = self.__pos
        result = self.skip(pattern, False)
        self.__pos = pos
        return result

    def skip(self, pattern, strict=True, name=None):
        return self.get(pattern, strict, name) is not None

    def format_line_parse_error(self, message):
        return "%s\n  File '%s', line %d\n    %s" % (message, self.__file, self.__linenum, self.get_line())

    def format_pattern_parse_error(self, name):
        parser = ConfigParser(self.__file, self.__pos)

        if not self.__initial:
            parser.skip(r"( |\t)+", False)

        result = None
        if parser.test(r"\r?\n"):
            result = "end of line"
        else:
            if parser.test(r"\W"):
                result = "'%s'" % parser.get(r"\W", forward="")
            else:
                result = "'%s'" % parser.get(r"\w(?:\w|-)+", forward="")

        return self.format_line_parse_error("Expected %s but got %s." % (name, result))

    def get(self, pattern, strict=True, name=None):
        if self.check_end():
            if strict:
                if name is None:
                    name = "'%s'" % pattern
                raise RuntimeError(self.format_pattern_parse_error(name))
            else:
                return None

        pos = self.__pos

        if not self.__initial:
            ch = str(self.__input[self.__pos])
            while ch == " " or ch == "\t":
                self.__pos += 1
                ch = str(self.__input[self.__pos])

        result = re.match(pattern, self.__input[self.__pos:])
        if result is None:
            self.__pos = pos
            if strict:
                if name is None:
                    name = "'%s'" % pattern
                raise RuntimeError(self.format_pattern_parse_error(name))
            else:
                return None

        match = result.group(0)
        groups = result.groups()

        self.__initial = False
        self.__pos += len(match)

        if len(groups) > 0:
             return [match] + list(group for group in groups)

        return match

    def get_line(self):
        return self.__input[self.__line:].splitlines()[0]

    def end_line(self, pattern=None, strict=True):
        pos = self.__pos

        if pattern is not None:
            if not self.skip(pattern, strict):
                self.__pos = pos
                return False

        if not self.check_end():
            if not self.skip(r"\r?\n", strict, "end of line"):
                self.__pos = pos
                return False

            self.__linenum += 1
            self.__line = self.__pos

            while self.skip(r"\r?\n", False):
                self.__linenum += 1
                self.__line = self.__pos

        self.__initial = True
        return True

    def check_indent(self, strict=True):
        if self.indent > 0:
            if not self.skip(r"(?:\t|\s{4,4}){%d,%d}(?=\S)" % (self.indent, self.indent), False):
                if strict and self.test(r"(?:\t|\s{4,4}){%d,%d}(?=\s)" % (self.indent, self.indent)):
                    raise RuntimeError(self.format_line_parse_error("Invalid indentation."))
                return False
        else:
            if strict and self.test(r" |\t"):
                raise RuntimeError(self.format_line_parse_error("Invalid indentation."))
            return not self.check_end()
        return True

    def get_indent(self):
        return self.__indent

    def set_indent(self, value):
        self.__indent = value

    def check_end(self):
        return self.__pos == len(self.__input)

    indent = property(get_indent, set_indent)


class Runnable(object):
    def run(self):
        pass


class Parsable(object):
    def parse(self, parser):
        pass


class Group(Runnable, Parsable):
    def __init__(self, name=None, parent=None, parser=None, dir=None):
        self.parent = parent
        self.name = name
        self.dir = dir if dir is not None else parent.dir
        self.ignore_failed = False
        self.ignore_non_existent = False
        self.modules = []
        self.errors = []
        if parser is not None:
            self.parse(parser)

    def get_root(self):
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    def get_path(self):
        from os.path import join
        fullname = self.fullname
        if fullname:
            return join(self.dir, fullname.replace(".", "/"))

    def get_exists(self):
        from os.path import exists, isdir
        return exists(self.get_path()) and isdir(self.get_path())

    def parse(self, parser):
        parser.end_line(strict=False)

        while parser.check_indent():
            identifier = parser.get(r"[a-zA-Z_](?:\w|\d)*", name="identifier")

            if identifier == "ignore":
                if parser.skip("failed", False):
                    self.ignore_failed = True
                    parser.end_line()
                elif parser.skip("non-existent", False):
                    self.ignore_non_existent = True
                    parser.end_line()
                else:
                    raise RuntimeError(parser.format_pattern_parse_error("'non-existent' or 'failed'"))

            elif identifier == "group":
                name = parser.get(r"[a-zA-Z_](?:\w|\d)*", name="identifier")
                if parser.test(r":"):
                    parser.end_line(":")
                    parser.indent += 1
                    self.modules.append(Group(name, self, parser, dir=self.dir))
                    parser.indent -= 1
                else:
                    parser.end_line()
                    self.modules.append(Group(name, self, dir=self.dir))

            elif identifier == "module":
                name = parser.get(r"[a-zA-Z_](?:\w|\d)*", name="identifier")
                if parser.test(r":"):
                    parser.end_line(":")
                    parser.indent += 1
                    self.modules.append(Module(name, self, parser, dir=self.dir))
                    parser.indent -= 1
                else:
                    parser.end_line()
                    self.modules.append(Module(name, self, dir=self.dir))

            else:
                raise RuntimeError(parser.format_line_parse_error("Unknown identifier '%s'." % identifier))

    def run(self):
        import sys, traceback

        result = True

        log.info("Starting group '%s'..." % self.name)

        try:
            __import__(self.fullname)
        except:
            log.error("Error occurred during initialization of package '%s'." % self.fullname, False)
            raise

        for module in self.modules:
            if not module.exists:
                if not self.ignore_non_existent:
                    self.root.errors.append("In group '%s':\n  Module '%s' does not exist." % (self.name, module.fullname))
                    log.error("Module '%s' does not exist." % module.fullname)
                else:
                    log.error("Module '%s' does not exist." % module.fullname, False)
                continue

            try:
                result = module.run() and result
            except:
                result = False

                if isinstance(module, Group):
                    log.error("Group '%s' failed." % module.name, False)
                else:
                    log.error("Module '%s' failed." % module.name, False)

                if not self.ignore_failed:
                    raise
                else:
                    log.message("".join(traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))

        log.ok("Group '%s' finished." % self.name)
        return result

    def get_fullname(self):
        parent = self.parent
        if parent is not None:
            name = parent.fullname
            if name is not None:
                return name + "." + self.name
        return self.name

    fullname = property(get_fullname)
    exists = property(get_exists)
    root = property(get_root)


class Module(Runnable, Parsable):
    def __init__(self, name, parent=None, parser=None, dir=None):
        self.name = name
        self.dir = dir if dir is not None else parent.dir
        self.parent = parent
        self.errors = []
        if parser is not None:
            self.parse(parser)

    def get_root(self):
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    def get_path(self):
        from os.path import join
        return join(self.dir, self.fullname.replace(".", "/") + ".py")

    def get_exists(self):
        from os.path import exists, isfile
        return exists(self.get_path()) and isfile(self.get_path())

    def parse(self, parser):
        pass

    def run(self):
        log.info("Starting module '%s'..." % self.name)
        try:
            __import__(self.fullname)
        except:
            import sys, traceback
            trace = "".join(map(lambda trace: "  " + trace, traceback.format_exception(sys.exc_type, sys.exc_value, sys.exc_traceback)))
            self.root.errors.append("In module '%s':\n%s" % (self.fullname, trace))
            raise

        log.ok("Module '%s' finished." % self.name)
        return True

    def get_fullname(self):
        parent = self.parent
        if parent is not None:
            name = parent.fullname
            if name is not None:
                return name + "." + self.name
        return self.name

    fullname = property(get_fullname)
    exists = property(get_exists)
    root = property(get_root)