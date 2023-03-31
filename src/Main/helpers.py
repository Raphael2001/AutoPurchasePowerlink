from src.Constas import POWER_LINK_URL
import requests
import json
from flask_restful import abort
from src.DatabaseModule.ApiLogs import *


class PowerLinkApi:

    def __init__(self, token, document_number ):
        self.token = token
        self.document_number = document_number
        self.headers = self.create_headers()


    def create_headers(self):
        return {"Content-type": "application/json",
                "tokenid": self.token}

    def update_client(self, account_id):
        url = POWER_LINK_URL + f"record/account/{account_id}"
        function_name = "PowerLink - update client"
        payload = {
            "pcflastorderid": str(self.document_number)
        }

        response = requests.put(url=url, data=json.dumps(payload), headers=self.headers)
        is_success, data = handle_response(response, payload, self.headers, function_name, self.document_number)
        if is_success:
            return data
        else:
            return False

    def get_client_details(self, account_id):
        # get client details from powerlink by account id
        url = POWER_LINK_URL + f"record/1/{account_id}"
        response = requests.get(url=url, headers=self.headers)
        payload = {"account_id": account_id}
        function_name = "PowerLink - get client"
        is_success, data = handle_response(response, payload, self.headers, function_name, self.document_number)
        if is_success:
            return data
        else:
            return False

    def get_documents(self):
        url = POWER_LINK_URL + "query"
        function_name = "PowerLink - get documents"
        payload = {
            "objecttype": 90,
            "page_size": 50,
            "page_number": 1,
            "fields": "*",
            "query": f"(documentnumber = {self.document_number})"
        }
        response = requests.post(url=url, data=json.dumps(payload), headers=self.headers)
        is_success, data = handle_response(response, payload, self.headers, function_name, self.document_number)
        if is_success:
            return data["data"]["Data"]
        else:
            return False

    def create_purchase(self, product, seller, outside_selling_value, agent):
        url = POWER_LINK_URL + "record/33"
        function_name = "PowerLink - create purchase"

        payload = {
            "productid": product.product_id,
            "accountid": product.account_id,
            "quantity": product.quantity,
            "price": product.item_price,
            "description": product.description,
            "pcforderid": self.document_number,  # מספר הזמנה
            "pcfpurchasedate": product.date,  # תאריך קנייה
            "pcfseller": seller,  # מוכר
            "pcfsystemfield89": outside_selling_value  # מכירות חול
        }
        if agent:
            payload["pcfsystemfield110"] = agent  # סוכן
        response = requests.post(url=url, data=json.dumps(payload), headers=self.headers)
        is_success, data = handle_response(response, payload, self.headers, function_name, self.document_number)
        if is_success:
            return data
        else:
            return False


def handle_response(response, payload, headers, function_name, document_number):
    is_success = True
    if 200 <= response.status_code < 400:
        json_response = json.loads(response.content)
        response_data = json_response

    else:
        response_data = response.content.decode("utf-8")
        is_success = False

    add_api_log(payload, function_name, response.status_code, response_data, headers, document_number)
    return is_success, response_data


def abort_api(status_code, message, body=None):
    abort(status_code, status="ERROR", body=body, message=message)
