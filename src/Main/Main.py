import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from src.PurchaseModule.Purchase import Purchase

app = Flask(__name__)
api = Api(app)
CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type; utf-8'
app.config['Access-Control-Allow-Origin'] = '*'


api.add_resource(Purchase, '/api/v1/purchase')

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc', host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
