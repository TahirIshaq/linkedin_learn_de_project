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