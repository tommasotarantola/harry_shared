import pymongo
import pytz
import logging


class MongoDB:
    def __init__(self, db_path, db_name, username=None):
        self.client = pymongo.MongoClient(db_path, serverSelectionTimeoutMS=5000)
        self.client.server_info()
        db_names = [db for db in self.client.list_database_names()]
        if db_name not in db_names: raise Exception(f"DB not found: {db_name}")
        self.db = self.client[db_name]
        self.utc = pytz.UTC
        self.logger = logging.getLogger()

    @staticmethod
    def cst_flat_dict(dictionary_list, key):
        return [dictionary.get(key) for dictionary in dictionary_list]

    def cst_mongo_find(self, collection, query={}, projection={}, mongo_id=False, limit=None):
        if mongo_id is False: projection["_id"] = 0
        mongo_results = self.db[collection].find(query, projection)
        if limit is not None:
            mongo_results = mongo_results.limit(limit)
        return [x for x in mongo_results]

    def cst_mongo_update(self, collection, query, update):
        result = self.db[collection].update_many(query, update)
        self.logger.info(f"Founded: {result.raw_result['n']} - Updated: {result.raw_result['nModified']}")
        return result

    def cst_mongo_delete(self, collection, query):
        results = self.cst_mongo_find(collection, query)
        if len(results) > 10:
            user_confirm = input(f'High number of documents: {len(results)}. Needed confirmation (y)')
            if user_confirm != "y":
                return False
        result = self.db[collection].delete_many(query)
        self.logger.warning(f"Removed: {result.deleted_count} documents")
        return result
