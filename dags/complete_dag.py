# Move data from source postgres to destination postgres

import pendulum
from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
from random import randint
import logging
from tempfile import NamedTemporaryFile

SOURCE_DB_CONN_ID = "source_db"
AWS_CONN_ID = "minio_s3"

@dag(dag_id="pg_pg_elt", start_date=datetime(2023, 8, 1), schedule=None, catchup=False, tags=["dynamic-mapping", "elt", "pg"])
def pg_pg_elt(batch_size=10000, total_batches=10):

    @task(task_id="Convert ")
    def fetch_postgres_data(table_name, batch_number):
        postgres_hook = PostgresHook(postgres_conn_id="postgres_conn_id")
        
        offset = batch_size * batch_number
        sql = f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
        df = postgres_hook.get_pandas_df(sql)
        logging.into(f"Fetched batch {batch_number} with {len(df)} rows from POstgreSQL")
        return df

    # Format the table names and queries as key value pairs i.e. dict
    @task(task_id='format_names')
    def format_names(data):
        result = []
        for value in data:
            table_name = value[0]
            query = f"SELECT * FROM {table_name};"
            result.append({"query": query, "s3_key": table_name})
        return result

    queries = format_names(get_table_names.output)

    sql_to_s3_task_with_groupby = SqlToS3Operator.partial(
        task_id="sql_to_s3_with_groupby_task",
        sql_conn_id=SOURCE_DB_CONN_ID,
        aws_conn_id=AWS_CONN_ID,
        s3_bucket='test-b',
        replace=True,
        file_format="csv",
    ).expand_kwargs(
        queries
    )


sql_expand_test()