from flask_restful import Resource, reqparse

from src.Main.helpers import PowerLinkApi, add_api_log
from src.Constas import TAX_RATE

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
        self.power_link: PowerLinkApi = None

    def create_purchases(self):
        data_array = self.power_link.get_documents()
        if not data_array:
            return False

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
                client = self.power_link.get_client_details(account_id)
                if not client:
                    return False

                customer_owner = client['data']['Record']["pcfcustomerowner"]
                originating_lead_code = client['data']['Record']["originatingleadcode"]
                seller = get_seller_by_customer_owner(customer_owner)
                agent = get_agent_by_originating_lead_code(originating_lead_code)
                purchase_data = self.power_link.create_purchase(product, seller, outside_selling, agent)
                client_data = self.power_link.update_client(account_id)

                if purchase_data is False or client_data is False:
                    return False

        return True

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('documentnumber', required=True, location='json',
                            help="documentnumber is missing")
        parser.add_argument('token', required=True, location='json',
                            help="token is missing")
        parser.add_argument('taxvalue', required=True, location='json',
                            help="taxvalue is missing")
        args = parser.parse_args()
        # add args
        self.document_number = args["documentnumber"]
        add_api_log(args, "Api - Purchase", document_number=self.document_number)

        self.tax_value = args['taxvalue']

        self.power_link = PowerLinkApi(args["token"], self.document_number)
        response = self.create_purchases()
        if response:
            return {
                'statuscode': 200,
                'body': {},
                'message': "",
            }
        else:
            return {
                'statuscode': 200,
                'body': {},
                'message': "problem with the request",
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
