from bson import ObjectId
import pymongo as pm


def main():
    URL = 'mongodb://kraftwerk28:271828@localhost/tgai28?authSource=admin'
    client = pm.MongoClient(URL)
    main_coll = client['tgai28']['config']
    result = main_coll.update_one(
        {'_id': ObjectId('5e1d005989a3111d89094278')},
        {'$set': {'frame_type': 'single'}}
    )
    client.close()


if __name__ == '__main__':
    main()
