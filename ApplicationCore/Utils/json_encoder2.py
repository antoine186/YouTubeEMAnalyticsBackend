from json import JSONEncoder

class GenericJsonEncoder2(JSONEncoder):
        def default(self, o):
            try:
                  return o.__dict__
            except:
                  return None
