
from flask import request



def get_token():
    req = request.headers.get("Authorization", None)
    token = req.split()[1]

    return token
