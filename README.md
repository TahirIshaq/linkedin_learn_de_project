# linkedin_learn_de_project
Linkedin learning data engineering end to end project

## Usage
1. `git clone https://github.com/TahirIshaq/linkedin_learn_de_project`
2. `docker compose up -d`
3. `pip install -r requirements.txt`
4. `. ./s3_env_vars.sh && . ./source_db_vars.sh && . ./destination_db_vars.sh`
5. `python elt.py`

### (Optional) Use a python virtual environment
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`

### (Optional) Use a conda environment
1. `conda env create -f conda_env.yml`
2. `conda activate my_env`

open `localhost:9001` and login using the s3 credentials in `s3.env`. The default ones are: `username: admin, password: admin12345`. Go to the bucket `data` and its directory `raw_data`. Here the postgres tables are present in parquet format.

### Verifying the data in the destination database
#### Option 1
Login to the destination database container: `docker exec -it destination_db bash`
Login to the destination database server: `psql "postgresql:test:test@localhost:5432/test-db"`
List all the tables: `\d`
### Option 2
Add a pg admin container in `docker-compose.yml`, access the destination database and list the tables.
### Option 3
Add a function in `elt.py` that queries the destination database and verify the contents.

## Part 2 (Data Transformation)
### Project initilization
Since we used postgres as our destination database, we will use dbt postgres connector to transform the data.
`dbt init transform_data` will create a dbt project called **transform_data**. This will create the dbt project file structure.
`transform_data/dbt_project.yml` contains the dbt project configuration e.g. path of `model, tests, macros, profiles etc`. Project initialization also creates a connection profile which in this case is a postgres connector. The default localtion of profiles is `~/.dbt/profiles.yml`. For this project, `profiles.yml` was saved in `transform_data/config/profiles.yml`. `export DBT_PROFILES_DIR=/workspaces/linkedin_learn_de_project/transform_data/config/` will change the path of `profiles.yml`.
### Configuring profiles.yml
To make our credentials more secure, we will set the profiles credentials using jinja. The credentials will be read from the environment variables(which need to be set). Make sure to cast/convert any non string variables e.g. port number.
### Testing the connection
Run `dbt debug` in dbt directory to test the profile. To run this command from anywhere set the path of `dbt_project.yml` in `DBT_PROJECT_DIR`.
### Models
Models are `.sql` files i.e. containing sql commands(only SELECT). The modelling is divided in 2 logical parts `staging` and `core/marts`.
All models can either be a view(default) or a table. The output can be changed by configuring `dbt_project.yml` or the model file individually (at the start of the model file).

**Staging**

This is first step in data modelling and everything is a view.

**Marts/Core**

This is the final step in data modelling and everything(all tables/.sql files) is/are a table.

### DBT packages
`touch transform_data/packages.yml` will create the packages file.
The package [codegen](https://hub.getdbt.com/dbt-labs/codegen/latest/) is used to generate dbt code.
```
packages:
    - package: dbt-labs/codegen
      version: 0.12.1
```
Install the package `dbt deps`
Generate the model information of the models that have that have been completed `dbt --quiet run-operation generate_model_yaml --args '{"model_names": ["stg_customers", "stg_orders"]}' > models/staging/stg_models.yml`. There are 2 options either have 2 yml file 1 for model details and 1 for source or just copy the models details to schemy.yml and delete the file.
After this, [tests](https://docs.getdbt.com/docs/build/data-tests) can be added for each column

To have a look at the compiled code of models `dbt compile`.
The compiled code can be found in `transform_data/target/compiled/stg_orders`
To apply the compiled model `dbt build`. This will run a collection of commands including `dbt compile`
Run `dt clean` and then commit the changes. This will remove any installed packages hence reducing size(I think)