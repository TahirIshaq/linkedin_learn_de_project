import logging
import pendulum
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from airflow.decorators import dag, task, task_group
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

SOURCE_DB_CONN_ID = "source_db"

# Configure logger
logger = logging.getLogger(__name__)

@dag(dag_id="chaltay_raho", start_date=datetime(2023, 8, 1), schedule=None, catchup=False)
def load_save():

    SQLExecuteQueryOperator(
        task_id="table_names",
        sql=f"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
    )
    @task
    def get_table_names(con_id):
        """Returns all the tables in the schema"""
        table_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
        hook = PostgresHook(postgres_conn_id=con_id)    # Postgres connector needs to be created in airflow
        conn = hook.get_conn()
        table_names = None
        with conn.cursor() as curs:
            curs.execute(table_query)
            table_names = curs.fetchall()
            print("raw table names: ", table_names)
            get_names = lambda names: [name[0] for name in names]
            table_names = get_names(table_names)
        conn.close()
        return table_names
    
    @task(task_id="get_col_names")
    def get_col_names(con_id, table_name):
        """Returns the column names of the table"""
        hook = PostgresHook(postgres_conn_id=con_id) # Postgres connector needs to be created in airflow
        conn = hook.get_conn()
        col_names = None
        col_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = \'{table_name}\';"
        col_names = None
        with conn.cursor() as curs:
            curs.execute(col_query)
            col_names = curs.fetchall()
            get_names = lambda names: [name[0] for name in names]
        conn.close()
        return col_names
    
    @task(task_id="")
    def get_all_table_details(con_id):
        """Returns the names of all tables in the database"""
        table_details = dict()
        table_names = get_table_names(con_id)
        for table_name in table_names:
            table_details[table_name] = get_table_col_names(conn, table_name)
        print(table_details)


    # t_names = get_table_names(SOURCE_DB_CONN_ID)
    # pr_inter = get_table_col_names(SOURCE_DB_CONN_ID, t_names)
    # tester = get_all_table_details(SOURCE_DB_CONN_ID)
    # #t_names >> pr_inter
    # tester

load_save()