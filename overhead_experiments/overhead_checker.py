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
connection_string = "mongodb://ec2-3-106-130-112.ap-southeast-2.compute.amazonaws.com:27017/"
db_name = "experiment0"
collection_name = "uniform"
REP = 30
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
        range_query = generate_range_query()

        for n in range(n_disjunction):
            disjunctions.append(range_query)

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

    execution_time_lst = []
    for i in range(REP):
        client[db_name].command(
            {"planCacheClear": collection_name}
        )
        query_explain = collection.find(query, projection).explain()
        exec_t = query_explain["executionStats"]["executionTimeMillis"]
        execution_time_lst.append(int(exec_t))

    statistics_df = pd.DataFrame(zip(cold_runs, hot_runs, execution_time_lst), columns=["cold_runs", "hot_runs", "exec_t"])
    statistics_df = statistics_df[statistics_df.apply(lambda x: (x - x.mean()).abs() < (2 * x.std())).all(1)]
    avg_overhead = statistics_df["cold_runs"].mean() - statistics_df["hot_runs"].mean()
    avg_exec_t = statistics_df["exec_t"].mean()
    return avg_overhead, avg_exec_t


if __name__ == '__main__':

    client = establish_connection(connection_string)
    collection = client[db_name][collection_name]
    create_indexes(collection)
    selectivity_exp_path = "selectivity-experiments-6/"
    n_plans_exp_path = "n-plans-experiments-6/"

    experiment_dir = join(result_dir, selectivity_exp_path)
    os.makedirs(os.path.dirname(experiment_dir), exist_ok=True)
    a_selectivity_selections = [0.000001, 0.000005, 0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005,
                                0.01, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1]
    b_selectivity_selections = [1] * len(a_selectivity_selections)
    n_disjunction = 5
    max_disjunction_solutions = 50
    client.admin.command(({"setParameter": 1, "internalQueryEnumerationMaxOrSolutions": max_disjunction_solutions}))
    id = 0
    overheads = []
    overhead_per_plan = []
    execution_time_lst = []
    for (a_s, b_s) in zip(a_selectivity_selections, b_selectivity_selections):
        client[db_name].command({"planCacheClear": collection_name})
        avg_overhead, avg_exec_t = measure_overhead(collection=collection,
                         n_disjuction=n_disjunction,
                         a_selectivity=a_s,
                         b_selectivity=b_s,
                         n_docs=N_DOCS,
                         fig_path=join(experiment_dir, "{}-a-{:.2f}-b-{:.2f}.html".format(id, a_s, b_s)))
        overheads.append(avg_overhead)
        overhead_per_plan.append(avg_overhead / (max_disjunction_solutions + 3))
        execution_time_lst.append(avg_exec_t)
        id += 1
    fig = go.Figure()

    fig.add_trace(go.Bar(name="Overhead for all plans",
                             x=[str(x) for x in a_selectivity_selections],
                             y=overheads,
                             # mode='lines',
                             # line=dict(color='#d62728', width=4)
                         ))
    fig.add_trace(go.Bar(name="Average overhead per plan",
                             x=[str(x) for x in a_selectivity_selections],
                             y=overhead_per_plan,
                             # mode='lines',
                             # line=dict(color='#1f77b4', width=4)
                         ))

    fig.update_layout(title="Overhead vs Selectivity",
                      xaxis_title='Selectivity of the query',
                      yaxis_title='Time in Milliseconds(ms)',
                      title_x=0.5)
    fig.write_html(join(experiment_dir, "overhead-vs-selectivity.html"))

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Overhead Ratio",
                             x=[str(x) for x in a_selectivity_selections],
                             y=[round(o / e, 3) for (o, e) in zip(overhead_per_plan, execution_time_lst)],
                         ))
    fig.update_layout(title="Overhead Ratio vs Selectivity",
                      xaxis_title='Selectivity of the query',
                      yaxis_title='Overhead / Execution time',
                      title_x=0.5)
    fig.write_html(join(experiment_dir, "overhead-ratio-vs-selectivity.html"))

    experiment_dir = join(result_dir, n_plans_exp_path)
    os.makedirs(os.path.dirname(experiment_dir), exist_ok=True)
    a_selectivity = 0.5
    b_selectivity = 1
    n_disjunction = 5
    max_disjunction_solutions = [x * 5 for x in range(11)]
    id = 0
    overheads = []
    overhead_per_plan = []
    execution_time_lst = []
    for n in max_disjunction_solutions:
        client.admin.command(({"setParameter": 1, "internalQueryEnumerationMaxOrSolutions": n}))
        client[db_name].command({"planCacheClear": collection_name})
        avg_overhead, avg_exec_t = measure_overhead(collection=collection,
                                        n_disjuction=n_disjunction,
                                        a_selectivity=a_selectivity,
                                        b_selectivity=b_selectivity,
                                        n_docs=N_DOCS,
                                        fig_path=join(experiment_dir, "{}-max-solutions-{}.html".format(id, n)))
        overheads.append(avg_overhead)
        overhead_per_plan.append(avg_overhead / (n + 3))
        execution_time_lst.append(avg_exec_t)
        id += 1
    fig = go.Figure()

    fig.add_trace(go.Bar(name="Overhead for all plans",
                             x=max_disjunction_solutions,
                             y=overheads,
                             # mode='lines',
                             # line=dict(color='#d62728', width=4)
                         ))
    fig.add_trace(go.Bar(name="Average overhead per plan",
                             x=max_disjunction_solutions,
                             y=overhead_per_plan,
                             # mode='lines',
                             # line=dict(color='#1f77b4', width=4)
                         ))
    fig.update_layout(title="Overhead vs # of query plans",
                      xaxis_title='# of query plans',
                      yaxis_title='Time in Milliseconds(ms)',
                      title_x=0.5)
    fig.write_html(join(experiment_dir, "overhead-vs-n-plans.html"))

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Overhead Ratio",
                             x=max_disjunction_solutions,
                             y=[o / e for (o, e) in zip(overhead_per_plan, execution_time_lst)],
                         ))
    fig.update_layout(title="Overhead Ratio vs # of query plans",
                      xaxis_title='# of query plans',
                      yaxis_title='Overhead / Execution time',
                      title_x=0.5)
    fig.write_html(join(experiment_dir, "overhead-ratio-vs-n-plans.html"))
