import re
from plamee import log

class Parser(object):
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

    def skip(self, pattern, strict=True):
        return self.get(pattern, strict) is not None

    def get(self, pattern, strict=True):
        if self.check_end():
            if strict:
                raise RuntimeError("Parse error")
            else:
                return None

        pos = self.__pos

        if not self.__initial:
            while str(self.__input[self.__pos]) == " ":
                self.__pos += 1

        result = re.match(pattern, self.__input[self.__pos:])
        if result is None:
            self.__pos = pos
            if strict:
                raise RuntimeError("Parse error")
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
            if not self.skip(r"\r?\n", strict):
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
                    raise RuntimeError("Invalid indentation at line %s:%d '%s'" % (self.__file, self.__linenum, self.get_line()))
                return False
        else:
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
        while parser.check_indent():
            if parser.skip("ignore", False):
                if parser.skip("failed", False):
                    self.ignore_failed = True
                    parser.end_line()
                elif parser.skip("non-existent", False):
                    self.ignore_non_existent = True
                    parser.end_line()
                else:
                    raise RuntimeError("Invalid ignore flag in line '%s'" % parser.get_line())

            elif parser.skip("group", False):
                name = parser.get(r"\w(?:\w|\d)*")
                if parser.test(r":"):
                    parser.end_line(":")
                    parser.indent += 1
                    self.modules.append(Group(name, self, parser, dir=self.dir))
                    parser.indent -= 1
                else:
                    self.modules.append(Group(name, self, dir=self.dir))

            elif parser.skip("module", False):
                name = parser.get(r"\w(?:\w|\d)*")
                if parser.test(r":"):
                    parser.end_line(":")
                    parser.indent += 1
                    self.modules.append(Module(name, self, parser, dir=self.dir))
                    parser.indent -= 1
                else:
                    parser.end_line()
                    self.modules.append(Module(name, self, dir=self.dir))

            else:
                raise RuntimeError("Unknown command %s" % parser.get(r".*?(?=\s)", False))

    def run(self):
        import sys, traceback

        result = True

        log.info("Starting group '%s'..." % self.name)

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