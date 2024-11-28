import logging
import pendulum
import pandas as pd
from sqlalchemy import create_engine
from airflow.decorators import dag, task, task_group
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

SOURCE_DB_CONN_ID = "source_db"

# Configure logger
logger = logging.getLogger(__name__)



@dag(
    dag_id="postgres_load",
    schedule="@once",
    start_date=pendulum.today('UTC').add(days=-1),
    catchup=False,
    description="Loading data from the source database"
)
def load_data():

    start = DummyOperator(task_id="start")
    
    @task_group(group_id='get_table_details')
    def get_table_details():

        @task(task_id="get_table_names")
        def get_table_names(con_id, write_key, schema_name="public", **kwargs):
            """Returns all the tables in the schema"""
            table_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema=\'{schema_name}\' AND table_type='BASE TABLE';"
            hook = PostgresHook(postgres_conn_id=con_id) # Postgres connector needs to be created in airflow
            conn = hook.get_conn()
            table_names = None
            with conn.cursor() as curs:
                curs.execute(table_query)
                table_names = curs.fetchall()
                get_names = lambda names: [name[0] for name in names]
                table_names = get_names(table_names)
            conn.close()
            kwargs["ti"].xcom_push(key=write_key, value=table_names[0])
    
        @task(task_id="get_table_col_names")
        def get_table_col_names(con_id, **kwargs):
            """Returns the column names of the table"""
            table_names = kwargs["ti"].xcom_pull(key="tvar_1", task_ids="get_table_names")
            print("The tables names are:", table_names)
            # hook = PostgresHook(postgres_conn_id=con_id) # Postgres connector needs to be created in airflow
            # conn = hook.get_conn()
            # table_details = {}
            # for table_name in tables_names:
            #     col_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = \'{table_name}\';"
            #     col_names = None
            #     with conn.cursor() as curs:
            #         curs.execute(col_query)
            #         col_names = curs.fetchall()
            #         get_names = lambda names: [name[0] for name in names]
            #         table_details[table_name] = get_names(col_names)
            # con.close()
            # kwargs["task_instance"].xcom_push(key=write_key, value=table_details)
    
        get_table_names(SOURCE_DB_CONN_ID, "tvar_1") >> get_table_col_names(SOURCE_DB_CONN_ID)

        # @task(task_id="get_all_table_details")
        # def get_all_table_details(con, schema_name="public", **kwargs):
        #     """Returns the names of all tables in the database"""
        #     table_details = dict() 
        #     get_table_names(con, schema_name)
        #     table_names = kwargs["task_instance"].xcom_pull(key="table_names", task_ids="get_table_names")
        #     print(table_names)
        #     for table_name in table_names:
        #         table_details[table_name] = get_table_col_names(con, table_name)
        #     return table_details
        
    # @task(task_id="table_to_pd_df")
    # def table_to_pd_df(conn, table_name, schema_name, table_cols):
    #     """Convert table to pandas dataframe and returns it"""
    #     query = f"SELECT * FROM {schema_name}.{table_name};"
    #     df = None
    #     with conn.cursor() as curs:
    #         curs.execute(query)
    #         rows = curs.fetchall()
    #         df = pd.DataFrame(rows, columns=table_cols)
    #     return df
    
    # @task(task_id="upload_to_postgres")
    # def upload_to_postgres(conn):
    #     """Upload pd dataframe to postgres"""
    #     query = f"SELECT * FROM {schema_name}.{table_name};"
    #     df = None
    #     with conn.cursor() as curs:
    #         curs.execute(query)
    #         rows = curs.fetchall()
    #         df = pd.DataFrame(rows, columns=table_cols)
    #         with create_engine.connect() as con:
    #             df.to_sql(name=table_name)
    #     return df

    end = DummyOperator(task_id="end")

    table_names = get_table_details()

    start >> table_names >> end

load_data()