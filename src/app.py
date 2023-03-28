import json
import os
import requests
from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type; utf-8'
app.config['Access-Control-Allow-Origin'] = '*'

POWER_LINK_URL = "https://api.powerlink.co.il/api/"
POWER_LINK_TOKEN = "2d2844c9-d94f-416d-898e-cbc30ddaf6b2"
TAX_RATE = 1.17

HEADERS = {"Content-type": "application/json",
           "tokenid": POWER_LINK_TOKEN}

drop_down_list_representative = {
    10: "רפאל",
    2: "מוריס",
    1: "מארק",
    9: "ניצה חנה מטילד",
    8: "ז׳רמי",
    11: "פילץ",
}


def get_documents(document_number):
    url = POWER_LINK_URL + "query"

    payload = {
        "objecttype": 90,
        "page_size": 50,
        "page_number": 1,
        "fields": "*",
        "query": f"(documentnumber = {document_number})"
    }
    response = requests.post(url=url, data=json.dumps(payload), headers=HEADERS)
    return json.loads(response.content)["data"]["Data"]


def get_client_details(account_id):
    # get client details from powerlink by account id
    url = POWER_LINK_URL + f"record/1/{account_id}"
    response = requests.get(url=url, headers=HEADERS)
    return json.loads(response.content)


def create_purchase(product, seller, outside_selling_value, doc_number, agent):
    url = POWER_LINK_URL + "record/33"
    payload = {
        "productid": product.product_id,
        "accountid": product.account_id,
        "quantity": product.quantity,
        "price": product.item_price,
        "description": product.description,

        "pcforderid": doc_number,  # מספר הזמנה
        "pcfpurchasedate": product.date,  # תאריך קנייה
        "pcfseller": seller,  # מוכר
        "pcfsystemfield89": outside_selling_value  # מכירות חול
    }
    if agent:
        payload["pcfsystemfield110"] = agent  # סוכן
    response = requests.post(url=url, data=json.dumps(payload), headers=HEADERS)
    return json.loads(response.content)


def update_client(doc_number, account_id):
    url = POWER_LINK_URL + f"record/account/{account_id}"

    payload = {
        "pcflastorderid": str(doc_number)
    }

    response = requests.put(url=url, data=json.dumps(payload), headers=HEADERS)
    return json.loads(response.content)


def get_seller_by_customer_owner(customer_owner):
    if customer_owner == 2:
        return "1"  # מוריס
    return "3"  # הומאוטריט לאב


def get_agent_by_originating_lead_code(originating_lead_code):
    if originating_lead_code is None:
        return None
    originating_lead_code = int(originating_lead_code)
    if originating_lead_code == 26:  # לקוחות אורנית
        return "9ddf1077-6c1e-444c-a71b-9c911b23810f"
    elif originating_lead_code == 16:  # מטפלת ליאורה אפשטיין
        return "b1bc99fb-24c4-4981-9ec1-7cb8a8f645ee"
    elif originating_lead_code == 23:  # פילץ
        return "0d98229c-ec80-4a8f-9b6c-31f293e14246"
    elif originating_lead_code == 41:  # מונק
        return "d8b1762d-a856-493d-b40e-43f3c7638350"
    else:
        return None


class Purchase(Resource):

    def __init__(self):
        self.document_number = ""
        self.tax_value = ""

    def create_purchases(self):
        data_array = get_documents(self.document_number)

        if int(float(self.tax_value)) > 0:
            divide_tax_by = 1
            outside_selling = ""

        else:
            divide_tax_by = TAX_RATE
            outside_selling = 1

        for product_data in data_array:
            if product_data["documenttypecode"] == 84:
                product_id = product_data["productid"]
                account_id = product_data["accountid"]
                item_total_price = product_data["itemtotalprice"]
                quantity = int(product_data["itemquantity"])
                description = product_data["description"]
                date = product_data["createdon"]
                date = date.rsplit('T')[0]

                product = Product(product_id, account_id, item_total_price, quantity, date, description, divide_tax_by)
                client = get_client_details(account_id)
                customer_owner = client['data']['Record']["pcfcustomerowner"]
                originating_lead_code = client['data']['Record']["originatingleadcode"]
                seller = get_seller_by_customer_owner(customer_owner)
                agent = get_agent_by_originating_lead_code(originating_lead_code)
                create_purchase(product, seller, outside_selling, self.document_number, agent)
                update_client(self.document_number, account_id)

    def post(self):
        global POWER_LINK_TOKEN
        global HEADERS
        parser = reqparse.RequestParser()
        parser.add_argument('documentnumber', required=True, location='json',
                            help="documentnumber is missing")
        parser.add_argument('token', required=True, location='json',
                            help="token is missing")
        parser.add_argument('taxvalue', required=True, location='json',
                            help="taxvalue is missing")
        # add args
        args = parser.parse_args()
        self.document_number = args["documentnumber"]
        self.tax_value = args['taxvalue']
        POWER_LINK_TOKEN = args["token"]
        HEADERS["tokenid"] = POWER_LINK_TOKEN
        self.create_purchases()
        return {
            'statuscode': 200,
            'body': POWER_LINK_TOKEN,
            'message': "",
        }


class Product:
    def __init__(self, product_id, account_id, item_total_price_without_tax, quantity, date, description,
                 divide_tax_by):
        self.product_id = product_id
        self.account_id = account_id
        self.item_price = (item_total_price_without_tax * (TAX_RATE / divide_tax_by))
        self.quantity = quantity
        self.date = date
        self.description = description

    def __str__(self):
        return f"The product id is {self.product_id} and the account id is {self.account_id}, the quantity is " \
               f"{self.quantity} and the total price is {self.item_price}, created on {self.date}"


api.add_resource(Purchase, '/api/v1/purchase')

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc', host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
