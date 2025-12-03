from fastapi import Request, Depends
from pymongo.database import Database


def get_db(request: Request) -> Database:
    return request.app.database
