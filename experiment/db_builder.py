import logging
import random
import pandas as pd
import json
from save_load import save_doc
from save_load import load_doc
from logger import logging_decorator


@logging_decorator
def build_db(client,
             db_name,
             collection_name,
             dataset_size,
             dataset_path,
             ):

    # Remove old data and indexes
    collection = client[db_name][collection_name]
    collection.drop_indexes()
    collection.drop()

    # Generate dataset
    generate_dataset(dataset_size, dataset_path)
    import_dataset(collection, dataset_path)
    create_indexes(collection)


@logging_decorator
def generate_dataset(dataset_size, dataset_path):
    a_list = [x for x in range(int(dataset_size))]
    b_list = [x for x in range(int(dataset_size))]
    random.shuffle(a_list)
    random.shuffle(b_list)
    save_doc(dataset_path, a_list, b_list, length=int(dataset_size))


@logging_decorator
def import_dataset(collection, dataset_path):
    rows = load_doc(dataset_path)
    df = pd.DataFrame(rows, columns=['a', 'b'])
    data_json = json.loads(df.to_json(orient="records"))
    collection.insert(data_json)


@logging_decorator
def create_indexes(collection):
    collection.create_index("a", name='aIdx')
    collection.create_index("b", name='bIdx')
    collection.create_index(keys=[("a", 1), ("b", 1)], name='coverIdx')
