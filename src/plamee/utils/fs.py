import os.path

def join_path(*args):
    if len(args) > 0:
        if len(args) > 1:
            return os.path.join(*args)
        else:
            return args[0]
    return "./"

def read(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        pass
    return None