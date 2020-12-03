from pymongo.errors import ConnectionFailure
from pymongo.errors import ServerSelectionTimeoutError
import pymongo
from logger import logging_decorator


@logging_decorator
def establish_connection(connection_string):
    """
    Establish connection between the client
    and the cloud-hosted mongodb using connection string
    """
    client = pymongo.MongoClient(connection_string)

    try:
        client.admin.command('ismaster')
    except ConnectionFailure:
        exit()

    return client
