import argparse
from datetime import datetime
from os import listdir
from os.path import isfile, join

from logger import init_logger
from db_builder import build_db
from config_reader import get_conf, show_conf
from db_connection import establish_connection
from query import generate_query
from save_load import load_query
from query_plan_executor import exec_query


def main(args, conf):
    logger = init_logger(conf['path']['log_file_path'])
    logger.info("=" * 10 + " Experiment Starts " + "=" * 10)
    show_conf(conf)

    client = establish_connection(conf['db']['connection_string'])
    db_name = conf['db']['db_name']
    collection_name = conf['db']['collection_name']
    dataset_size = int(conf['db']['dataset_size'])
    granularity = int(conf['visual']['granularity'])

    if args.builddb:
        build_db(client=client,
                 db_name=db_name,
                 collection_name=collection_name,
                 dataset_size=dataset_size,
                 dataset_path=conf['path']['dataset_path'])

    if args.generatequery:
        generate_query(collection=client[db_name][collection_name],
                       collection_name=collection_name,
                       granularity=granularity,
                       dataset_size=dataset_size,
                       repetition=int(conf['query']['repetition']),
                       query_dir=conf['path']['query_dir'],
                       grid_dir=conf['path']['grid_dir'])

    query_dir = join(conf['path']['query_dir'], collection_name)
    query_files_names = [fn for fn in listdir(query_dir) if isfile(join(query_dir, fn))]

    for fn in query_files_names:
        query = load_query(join(query_dir, fn))
        exec_query(collection=client[db_name][collection_name],
                   collection_name=collection_name,
                   granularity=granularity,
                   queries=query,
                   query_file_name=fn,
                   fig_dir=conf["path"]["fig_dir"],
                   grid_dir=conf["path"]["grid_dir"])

    if client:
        client.close()

    logger.info("=" * 10 + " Experiment Finished " + "=" * 10)


if __name__ == '__main__':
    # read arguments
    parser = argparse.ArgumentParser(description='This program evaluates the effectiveness of MongoDB query optimizer.')
    parser.add_argument('-b', '--builddb', action='store_true', help='builds database')
    parser.add_argument('-q', '--generatequery', action='store_true', help='generate queries for all experiments')
    args = parser.parse_args()
    conf = get_conf()
    main(args, conf)
