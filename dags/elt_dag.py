import pendulum
from datetime import datetime
from airflow.decorators import dag, task
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
from random import randint

SOURCE_DB_CONN_ID = "source_db"
AWS_CONN_ID = "minio_s3"
table_namesq = ['customers', 'orders', 'order_items', 'products']

@dag(dag_id="sql_expand_test", start_date=datetime(2023, 8, 1), schedule=None, catchup=False, tags=["dynamic-mapping"])
def sql_expand_test():

    # Get the names of the tables in the database schema
    get_table_names = SQLExecuteQueryOperator(
        task_id="get_table_names",
        conn_id=SOURCE_DB_CONN_ID,
        sql=f"SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';",
        show_return_value_in_logs=True
    )

    # # Format the table names and queries as key value pairs i.e. dict
    # @task(task_id='format_names')
    # def format_names(data):
    #     queries = [f"SELECT * FROM {name[0]};" for name in data]
    #     table_name = [name[0] for name in data]
    #     return [{"s3_key": table_name, "query": queries}]

    # Format the table names and queries as key value pairs i.e. dict
    @task(task_id='format_names')
    def format_names(data):
        result = []
        for value in data:
            table_name = value[0]
            query = f"SELECT * FROM {table_name};"
            result.append({"query": query, "s3_key": table_name})
        return result
    
    # Format the table names and queries as key value pairs i.e. dict
    # @task(task_id='format_table_names')
    # def format_table_names(data):
    #     # queries = [f"SELECT COUNT(*) FROM {name[0]};" for name in data]
    #     table_names = [name[0] for name in data]
    #     return table_names

    queries = format_names(get_table_names.output)
    # table_names = format_names(get_table_names.output)

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
    # get_table_data = SQLExecuteQueryOperator.partial(
    #     task_id=f"get_table_data",
    #     conn_id=SOURCE_DB_CONN_ID,
    #     show_return_value_in_logs=True
    # ).expand(
    #     sql=[f"""SELECT COUNT(*) FROM {table_name};""" for table_name in  ",".join(["{{ task_instance.xcom_pull(task_ids='format_names', key='return_value') }}"])]
    # )

    # @task
    # def get_sql_queries():
    #     query = [
    #         "SELECT COUNT(*) FROM customers;", 
    #         "SELECT COUNT(*) FROM orders;", 
    #         "SELECT COUNT(*) FROM order_items", 
    #         "SELECT COUNT(*) FROM products"
    #     ]
    #     return query
    
    # @task
    # def get_table_names():
    #     return ['customers', 'orders', 'order_items', 'products']
    
    # run_queries = SQLExecuteQueryOperator.partial(
    #     task_id=f"run_queries",
    #     conn_id=SOURCE_DB_CONN_ID,
    #     show_return_value_in_logs=True
    # ).expand(
    #     sql=names
    #     #parameters={"table_name": [get_table_names()]}
    # )

    # run_queries = SQLExecuteQueryOperator.partial(
    #     task_id=f"run_queries",
    #     conn_id=SOURCE_DB_CONN_ID,
    #     show_return_value_in_logs=True,
    #     sql="SELECT COUNT(*) FROM %(table_name)s;"
    # ).expand(
    #     parameters=[{"table_name": get_table_names()]
    # )

    # run_queries = SQLExecuteQueryOperator.partial(
    #     task_id=f"run_queries",
    #     conn_id=SOURCE_DB_CONN_ID,
    #     show_return_value_in_logs=True
    # ).expand(
    #     sql=queries
    # )

    #'{{ ti.xcom_pull(task_ids='return_greeting') }} friend! :)'

    # for idx, table_name in names:
    # for idx, name in enumerate(["{{ task_instance.xcom_pull(task_ids='format_names', key='return_value') }}"]):
    #     get_table_data = SQLExecuteQueryOperator.partial(
    #         task_id=f"get_table_data",
    #         conn_id=SOURCE_DB_CONN_ID,
    #         sql="SELECT COUNT(*) FROM {{ params.table_name }};"
    #     ).expand(
    #         parameters={"table_name": name}
    #     )
    # execute_sql_queries = SQLExecuteQueryOperator.partial(
    #     task_id="execute_sql_queries_for_table",
    #     sql="SELECT COUNT(*) FROM %(table_name)s;",  # Use partial mapping with table_name
    #     conn_id=SOURCE_DB_CONN_ID,
    #     autocommit=True  # Pass the list of tables as part of params
    # ).expand(
    #     parameters={"table_name": names}
    # )
    # @task(task_id="print_table_names")
    # def print_table_names(data_in):
    #     print(data_in)
    
 #   names >> get_table_data

sql_expand_test()