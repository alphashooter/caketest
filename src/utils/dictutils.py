def merge_objects(obj1, obj2):
    for key in obj2.keys():
        if key in obj1 and isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
            merge_objects(obj1[key], obj2[key])
        else:
            obj1[key] = obj2[key]
