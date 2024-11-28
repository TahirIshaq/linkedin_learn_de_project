# Loads data from the source postgres database, converts it to parquet and saves it to the s3 bucket.
# Just a crude way to load and store data from one place to another.

import os
import boto3
import logging
import psycopg2
import pandas as pd
import pyarrow as pa
from io import BytesIO
import pyarrow.parquet as pq
from sqlalchemy import create_engine
from botocore.exceptions import ClientError


def create_bucket(bucket_name, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                      #dest_conn = connect_db(destination_db_username, destination_db_password, destination_db_host, destination_db_port, destination_db_name)
                  CreateBucketConfiguration=location)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def connect_db(username, password, host, port, db_name):
    """Connect to the DB and return the connection"""
    conn = psycopg2.connect(f"postgresql://{username}:{password}@{host}:{port}/{db_name}")
    return conn


def get_table_names(conn, schema_name="public"):
    """Returns all the tables in the schema"""
    table_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema=\'{schema_name}\' AND table_type='BASE TABLE';"
    table_names = None
    with conn.cursor() as curs:
        curs.execute(table_query)
        table_names = curs.fetchall()
        get_names = lambda names: [name[0] for name in names]
        table_names = get_names(table_names)
    return table_names


def get_table_col_names(conn, table_name):
    """Returns the column names of the table"""
    col_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = \'{table_name}\';"
    col_names = None
    with conn.cursor() as curs:
        curs.execute(col_query)
        col_names = curs.fetchall()
        get_names = lambda names: [name[0] for name in names]
        col_names = get_names(col_names)
    return col_names


def get_all_table_details(conn, schema_name):
    """Returns the names of all tables in the database"""
    table_details = dict()
    table_names = get_table_names(conn, schema_name)
    for table_name in table_names:
        table_details[table_name] = get_table_col_names(conn, table_name)
    return table_details


def table_to_pd_df(conn, table_name, schema_name, table_cols):
    """Convert table to pandas dataframe and returns it"""
    query = f"SELECT * FROM {schema_name}.{table_name};"
    df = None
    with conn.cursor() as curs:
        curs.execute(query)
        rows = curs.fetchall()
        df = pd.DataFrame(rows, columns=table_cols)
    return df

def upload_io_postgres(conn):
    """Upload df to postgres"""
    with create_engine(conn).connect() as con:
        df.to_sql(name=table, con=con, if_exists="replace")
        print(f"{table} inserted in destination database")


def upload_to_s3(bucket_name, sub_dir, table_name, df):
    """Converts pandas DataFrame to parquet and uploads it to S3"""
    buf = BytesIO()
    df.to_parquet(buf, compression='gzip', engine='pyarrow')
    buf.seek(0)
    #file_name = pd.read_parquet(buf)
    table = pq.read_table(buf)
    root_path = f"{bucket_name}/{sub_dir}/{table_name}"
    s3 = pa.fs.S3FileSystem(scheme="http", endpoint_override="localhost:9000")
    pq.write_to_dataset(
        table,
        root_path=root_path,
        filesystem=s3
    )


def main():
    """The main function"""
    source_db_username = os.getenv("SOURCE_DB_USERNAME")
    source_db_password = os.getenv("SOURCE_DB_PASSWORD")
    source_db_host = os.getenv("SOURCE_DB_HOST")
    source_db_port = os.getenv("SOURCE_DB_PORT")
    source_db_name = os.getenv("SOURCE_DB_NAME")
    source_db_schema = os.getenv("SOURCE_DB_SCHEMA")
    bucket_name = os.getenv("AWS_BUCKET_NAME")

    destination_db_username = os.getenv("DESTINATION_DB_USERNAME")
    destination_db_password = os.getenv("DESTINATION_DB_PASSWORD")
    destination_db_host = os.getenv("DESTINATION_DB_HOST")
    destination_db_port = os.getenv("DESTINATION_DB_PORT")
    destination_db_name = os.getenv("DESTINATION_DB_NAME")
    destination_db_schema = os.getenv("DESTINATION_DB_SCHEMA")

    conn = connect_db(source_db_username, source_db_password, source_db_host, source_db_port, source_db_name)
    dest_conn = f"postgresql://{destination_db_username}:{destination_db_password}@{destination_db_host}:{destination_db_port}/{destination_db_name}"

    create_bucket(bucket_name)
    all_tables = get_all_table_details(conn, schema_name=source_db_schema)
    for table in all_tables:
        df = table_to_pd_df(conn, table, source_db_schema, all_tables[table])
        # pandas.DataFrame.to_sql only supports sqlite and SQLalchemy therefore could not use postgres connection.
        with create_engine(dest_conn).connect() as con:
            df.to_sql(name=table, con=con, if_exists="replace")
            print(f"{table} inserted in destination database")
        upload_to_s3(bucket_name, "raw_data", table, df)
    conn.close()


if __name__ == "__main__":
    main()
