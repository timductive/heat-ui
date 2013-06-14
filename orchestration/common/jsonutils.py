import json

def to_json(objects):
    """
    Converts a list of objects or a singular object to json.
    """
    try:
        iter(objects)
    except:
        jsonobj = {}
        for k, v in objects.__dict__.items():
            if k[0] != '_':
                jsonobj[k]=str(v)
    else:
        jsonobj = []
        for obj in objects:
            temp = {}
            for k, v in obj.__dict__.items():
                if k[0] != '_':
                    temp[k]=str(v)
            jsonobj.append(temp)
    return json.dumps(jsonobj)