# Purpose of the Database
The purpose of this database is to facilitate the understanding of user behaviour more specifically what songs different users are listening to. 


# How to run the Python script

1. Run the script `create_tables.py`
2. Run the script `etl.py`
3. Run the notebook `test.ipynb`

# Explanation of files in repository

- in the `data`folder is the raw data with logs and song data
- in the `sql_queries.py` are the sql statments to create and update the differnet tables of the database
- in the `create_tables.py` script the dimension and fact tables are resetted and newly created 
- in the `etl.ipynb` notebook the sql statements are tested to see if all tables are created and updated properly
- in the `etl.py` script is the final ETL piepline to process all the data

# Database Schema Desgin and ETL Pipeline 

The database schema is a star schema made up of the songplays table as a fact table and four dimension tables: songs, artists, users and time. 
The ETL pipeline processes the raw data and efficiently divides the information into the separate tables.