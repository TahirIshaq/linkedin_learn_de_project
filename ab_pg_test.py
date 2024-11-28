import airbyte as ab

if __name__ == "__main__":
    source = ab.get_source(
        "source-postgres",
        config={
            "host": "localhost",
            "port": 5432,
            "schema_name": "public",
            "username": "postgres",
            "password": "mysecretpassword",
            "database": "big-star-db"
        },
        docker_image = True,
        use_host_network = True
    )
    # source = ab.get_source(
    #     "source-postgres",
    #     config={
    #         "host": "172.17.0.1",
    #         "port": 5433,
    #         "schema_name": "public",
    #         "username": "test",
    #         "password": "test",
    #         "database": "test-db"
    #     }
    # )
    source.check()
    #print(source.get_available_streams())
    # source.select_all_streams()
    # result = source.read()
    # print(result)