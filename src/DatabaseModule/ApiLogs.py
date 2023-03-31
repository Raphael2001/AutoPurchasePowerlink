import time
from src.DatabaseModule.DataBase import apilogs_ref


def add_api_log(body, method_name, status_code=None, response=None, headers=None, document_number=None):
    data = {"payload": body, "last_updated": int(time.time()), "method_name": method_name,
            "document_number": document_number}
    if status_code:
        data["status_code"] = status_code
    if response:
        data["response"] = response
    if headers:
        data["headers"] = headers
    apilogs_ref.insert_one(data)
