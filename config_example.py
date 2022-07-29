import pymongo

host_ip: str = "IP Address"
port_number: int = 0000 # Port Number
database_name = "Database name"
user_name = "User name"
password = "Password"


def get_client():
    global host_ip, user_name, password
    connection = pymongo.MongoClient(f"mongodb://{user_name}:{password}@{host_ip}")
    return connection
