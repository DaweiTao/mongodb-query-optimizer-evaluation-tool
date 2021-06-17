from db_connection import establish_connection
from time import perf_counter_ns
from numpy.random import randint
import numpy as np
from pprint import pprint
import os
from os.path import join
import json
import plotly.graph_objects as go
import pandas as pd

result_dir = "overhead-result/"
connection_string = "mongodb://ec2-52-65-17-244.ap-southeast-2.compute.amazonaws.com:27017/"
db_name = "experiment0"
collection_name = "uniform"
REP = 100
N_DOCS = 1000000


# make sures the query plan of the given query is cached
def update_cache(client, query, projection):
    client[db_name].command(
        {
            "planCacheClear": collection_name
        }
    )
    print("Cache reset")

    collection = client[db_name][collection_name]

    for i in range(10):
        collection.find(query, projection)

    print("Cache updated")


def create_indexes(collection):
    collection.create_index("a", name='aIdx')
    collection.create_index("b", name='bIdx')
    collection.create_index(keys=[("a", 1), ("b", 1)], name='coverIdx')


def generate_query(n_disjunction, a_selectivity, b_selectivity, n_docs):
    def generate_range_query():
        doc_min = 0
        doc_max = n_docs - 1
        a_offset = int(n_docs * a_selectivity)

        if doc_max - a_offset <= doc_min:
            a_min = 0
        else:
            a_min = randint(doc_min, doc_max - a_offset)
        a_max = a_min + a_offset

        b_offset = int(n_docs * b_selectivity)

        if doc_max - b_offset <= doc_min:
            b_min = 0
        else:
            b_min = randint(doc_min, doc_max - b_offset)
        b_max = b_min + b_offset
        return {"a": {"$gte": a_min, "$lt": a_max}, "b": {"$gte": b_min, "$lt": b_max}}

    query_temp = None

    if n_disjunction == 0:
        query_temp = generate_range_query()
    elif n_disjunction >= 1:
        disjunctions = []

        for n in range(n_disjunction):
            disjunctions.append(generate_range_query())

        range_query = generate_range_query()
        query_temp = {
            "a": range_query["a"],
            "b": range_query["b"],
            "$or": disjunctions
        }

    print(json.dumps(query_temp).replace("\"", ""))

    return query_temp


def visualize_overhead(cold_run_df, hot_run_df, avg_overhead, df_len, fig_path):
    fig = go.Figure()
    cold_run_df['MA'] = cold_run_df.rolling(window=int(REP/10)).mean()
    hot_run_df['MA'] = hot_run_df.rolling(window=int(REP/10)).mean()
    fig.add_trace(go.Scatter(x=hot_run_df.index, y=hot_run_df.MA,
                             mode='lines',
                             name='Hot run MA',
                             fill="tonexty",
                             line=dict(color='#d62728', width=4)))
    fig.add_trace(go.Scatter(x=cold_run_df.index, y=cold_run_df.MA,
                             mode='lines',
                             name='Cold run MA',
                             fill="tonexty",
                             line=dict(color='#1f77b4', width=4)))
    fig.add_trace(go.Scatter(x=hot_run_df.index, y=hot_run_df.hot_runs,
                             mode='markers',
                             name='Hot run',
                             marker=dict(color='#d62728', size=2)))
    fig.add_trace(go.Scatter(x=cold_run_df.index, y=cold_run_df.cold_runs,
                             mode='markers',
                             name='Cold run',
                             marker=dict(color='#1f77b4', size=2)))

    fig.update_layout(title='AVG overhead: {:.2f} milliseconds(ms)'.format(avg_overhead),
                      xaxis_title='Repetition #',
                      xaxis=dict(range=[1, df_len]),
                      yaxis_title='Latency in Milliseconds(ms)',
                      title_x=0.5)
    fig.write_html(fig_path)


def measure_overhead(collection, n_disjuction, a_selectivity, b_selectivity, n_docs, fig_path):
    query = generate_query(n_disjuction, a_selectivity, b_selectivity, n_docs)
    projection = {"_id": 0, "a": 1, "b": 1}
    hot_runs = []
    update_cache(client, query, projection)

    for i in range(REP):
        start = perf_counter_ns()
        rest = collection.find(query, projection).next()
        finish = perf_counter_ns()
        t_diff = (finish - start)
        duration_ms = t_diff / 1000000
        hot_runs.append(duration_ms)
        # print("Hot run progress: {}%".format(round(i * 100 / REP)))

    cold_runs = []
    for i in range(REP):
        client[db_name].command(
            {"planCacheClear": collection_name}
        )
        start = perf_counter_ns()
        rest = collection.find(query, projection).next()
        finish = perf_counter_ns()
        diff = (finish - start)
        duration_ms = diff / 1000000
        cold_runs.append(duration_ms)
        # print("Cold run progress: {}%".format(round(i * 100 / REP)))

    print("drawing")

    cold_run_df = pd.DataFrame(cold_runs, columns=["cold_runs"])
    hot_run_df = pd.DataFrame(hot_runs, columns=["hot_runs"])

    def remove_outlier_iqr(df):
        Q1 = df.quantile(0.25)
        Q3 = df.quantile(0.75)
        IQR = Q3 - Q1
        df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).any(axis=1)]
        return df

    cold_run_df = remove_outlier_iqr(cold_run_df)
    hot_run_df = remove_outlier_iqr(hot_run_df)
    cold_run_len = cold_run_df.shape[0]
    hot_run_len = hot_run_df.shape[0]
    df_len = min([cold_run_len, hot_run_len])
    cold_run_df = cold_run_df.head(df_len).reset_index(drop=True)
    hot_run_df = hot_run_df.head(df_len).reset_index(drop=True)
    avg_overhead = cold_run_df["cold_runs"].mean() - hot_run_df["hot_runs"].mean()
    visualize_overhead(cold_run_df, hot_run_df, avg_overhead, df_len, fig_path)
    return avg_overhead


if __name__ == '__main__':

    client = establish_connection(connection_string)
    collection = client[db_name][collection_name]
    create_indexes(collection)

    experiment_dir = join(result_dir, "selectivity-experiments-3/")
    os.makedirs(os.path.dirname(experiment_dir), exist_ok=True)
    a_selectivity_selections = [0.1 * x for x in range(1, 11)]
    b_selectivity_selections = [1] * 10
    n_disjunction = 5
    max_disjunction_solutions = 50
    client.admin.command(({"setParameter": 1, "internalQueryEnumerationMaxOrSolutions": max_disjunction_solutions}))
    id = 0
    overheads = []
    for (a_s, b_s) in zip(a_selectivity_selections, b_selectivity_selections):
        client[db_name].command({"planCacheClear": collection_name})
        avg_overhead = measure_overhead(collection=collection,
                         n_disjuction=n_disjunction,
                         a_selectivity=a_s,
                         b_selectivity=b_s,
                         n_docs=N_DOCS,
                         fig_path=join(experiment_dir, "{}-a-{:.2f}-b-{:.2f}.html".format(id, a_s, b_s)))
        overheads.append(avg_overhead/53)
        id += 1
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a_selectivity_selections, y=overheads,
                             mode='lines',
                             fill="tonexty",
                             line=dict(color='#d62728', width=4)))
    fig.update_layout(title="Overhead vs Selectivity",
                      xaxis_title='Selectivity of the query',
                      yaxis_title='Latency in Milliseconds(ms)',
                      title_x=0.5)
    fig.write_html(join(experiment_dir, "summary.html"))

    # experiment_dir = join(result_dir, "n-candidates-experiments-2/")
    # os.makedirs(os.path.dirname(experiment_dir), exist_ok=True)
    # a_selectivity = 0.5
    # b_selectivity = 1
    # n_disjunction = 5
    # max_disjunction_solutions = [x * 5 for x in range(11)]
    # id = 0
    # overheads = []
    # for n in max_disjunction_solutions:
    #     client.admin.command(({"setParameter": 1, "internalQueryEnumerationMaxOrSolutions": n}))
    #     client[db_name].command({"planCacheClear": collection_name})
    #     avg_overhead = measure_overhead(collection=collection,
    #                                     n_disjuction=n_disjunction,
    #                                     a_selectivity=a_selectivity,
    #                                     b_selectivity=b_selectivity,
    #                                     n_docs=N_DOCS,
    #                                     fig_path=join(experiment_dir, "{}-max-solutions-{}.html".format(id, n)))
    #
    #     n += 3
    #     overheads.append(avg_overhead / n)
    #     id += 1
    # fig = go.Figure()
    # max_disjunction_solutions = [x + 3 for x in max_disjunction_solutions]
    # fig.add_trace(go.Scatter(x=max_disjunction_solutions, y=overheads,
    #                          mode='lines',
    #                          fill="tonexty",
    #                          line=dict(color='#d62728', width=4)))
    # fig.update_layout(title="Overhead vs # of query plans",
    #                   xaxis_title='# of query plans',
    #                   yaxis_title='Latency in Milliseconds(ms)',
    #                   title_x=0.5)
    # fig.write_html(join(experiment_dir, "summary.html"))
