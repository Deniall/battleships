from pymongo import MongoClient
import time

def get_current_epoch_datetime():
	# returns the number of seconds since the epoch
    return int(time.time())

class DatabaseClient:
	def __init__(self, db_name="battleship"):
		"""init the client and grab the database"""
		self.client = MongoClient()
		self.db = self.client[db_name]

	def add_object(self, collection_name, data):
		"""Add data (a Python dict) to collection <collection_name>"""
		data["last_edit"] = get_current_epoch_datetime()
		result = self.db[collection_name].insert_one(data)
		return result.inserted_id

	def update_objects(self, collection_name, condition, data):
		"""Takes data as a Python object and updates all fields included in that data in the original doc to the new values"""
		if "_id" in data: # cannot modify _id, so remove it from the data to be modified
			del data["_id"]
		data["last_edit"] = get_current_epoch_datetime()
		results = self.db[collection_name].update_many(condition, {"$set":data})
		return results.matched_count

	def update_object_by_id(self, collection_name, id, data):
		"""update the fields in the document of the given id with the dict as data"""
		num = self.update_objects(collection_name, {"_id":id}, data)
		return num

	def get_objects(self, collection_name, condition):
		"""get all objects in the specified collection that match the given condition"""
		results = self.db[collection_name].find(condition)
		return results

	def get_object_by_id(self, collection_name, id):
		"""get the object with the given id in the specified collection"""
		#results = self.get_objects(collection_name, {"_id":id})
		result = self.db[collection_name].find_one({"_id":id})
		return result

		
if __name__ == "__main__":
	my_client = DatabaseClient("battleship-test")
	id =  my_client.add_object("lol", {"name" : "jeremy", "data": {"haha" : "no"}})
	print id
	data =  my_client.get_object_by_id("lol", id)
	print data
	data["name"] = "Paddy"
	print data
	num = my_client.update_object_by_id("lol", id, data)
	print num
	data = my_client.get_object_by_id("lol", id)
	print data
