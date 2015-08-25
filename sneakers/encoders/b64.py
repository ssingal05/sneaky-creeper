import base64

# TODO add optional params?
requiredParams = {
    'encode': {
              },
    'decode': {
              }
    }

def encode(data, params=None):
    return base64.b64encode(data)

def decode(data, params=None):
    try:
        return base64.urlsafe_b64decode(str(data))
    except TypeError:
        return "b64 could not decode this message: it is improperly formatted"