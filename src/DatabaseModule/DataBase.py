import pymongo


client = pymongo.MongoClient("mongodb+srv://raphaelaboohi:Raph2001@logs.8cd6l1r.mongodb.net/?retryWrites=true&w=majority")
db = client.GeneralLogs

apilogs_ref = db.autopurchaselogs


