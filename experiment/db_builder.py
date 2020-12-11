import logging
import random
import pandas as pd
import json
import os.path
import numpy as np
from save_load import save_doc
from save_load import load_doc
from logger import logging_decorator
import scipy.stats as ss
import scipy.special as sps


@logging_decorator
def build_db(client,
             db_name,
             collection_name,
             distribution,
             dataset_size,
             dataset_dir,
             ):

    # Remove old data and indexes
    collection = client[db_name][collection_name]
    collection.drop_indexes()
    collection.drop()

    # Generate dataset
    dataset_file_name = "{}_dist.txt".format(distribution)
    dataset_path = os.path.join(dataset_dir, dataset_file_name)

    if distribution == 'uniform':
        generate_uniform_dataset(dataset_size, dataset_path)
    elif distribution == 'linear':
        generate_linear_dataset(dataset_size, dataset_path)
    elif distribution == 'normal':
        generate_normal_dataset(dataset_size, dataset_path)
    elif distribution == 'zipfian':
        generate_zipfian_dataset(dataset_size, dataset_path)

    import_dataset(collection, dataset_path)
    create_indexes(collection)


@logging_decorator
def generate_uniform_dataset(dataset_size, dataset_path):
    a_list = [x for x in range(int(dataset_size))]
    b_list = [x for x in range(int(dataset_size))]
    random.shuffle(a_list)
    random.shuffle(b_list)
    save_doc(dataset_path, a_list, b_list, length=int(dataset_size))


@logging_decorator
def generate_linear_dataset(dataset_size, dataset_path):
    a_list = [i for i in range(dataset_size)]
    pdf = np.array([i / 2 for i in range(dataset_size)])
    pdf = pdf / pdf.sum()
    b_list = np.random.choice(np.arange(len(pdf)), size=dataset_size, p=pdf)
    b_list = [int(b) for b in b_list]
    random.shuffle(a_list)
    random.shuffle(b_list)
    save_doc(dataset_path, a_list, b_list, length=int(dataset_size))


@logging_decorator
def generate_normal_dataset(dataset_size, dataset_path):
    a_list = [x for x in range(dataset_size)]
    rand_nums = dataset_size
    x = np.arange(-1 * rand_nums / 2, rand_nums / 2)
    xU, xL = x + 0.5, x - 0.5
    prob = ss.norm.cdf(xU, scale=12000) - ss.norm.cdf(xL, scale=12000)
    # normalize the probabilities so their sum is 1
    prob = prob / prob.sum()
    b_list = np.random.choice(x, size=dataset_size, p=prob)
    b_list = [int(b + rand_nums / 2) for b in b_list]
    random.shuffle(a_list)
    random.shuffle(b_list)
    save_doc(dataset_path, a_list, b_list, length=int(dataset_size))


@logging_decorator
def generate_zipfian_dataset(dataset_size, dataset_path):
    a_list = [i for i in range(dataset_size)]
    a = 2.
    x = np.arange(float(dataset_size) / 20, float(dataset_size))
    y = x ** (-a) / sps.zetac(a)
    pdf = y / y.sum()
    zeros = [0 for i in range(int(float(dataset_size / 20)))]
    pdf.tolist().extend(zeros)

    b_list = np.random.choice(np.arange(len(pdf)), size=dataset_size, p=pdf)
    b_list = [int(b) for b in b_list]
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
