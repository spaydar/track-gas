'''
This file houses all SQL queries that are executed in the project.
They are written here for purposes of modularity and ease of maintenance.

Note:
    Query arguments are formatted as ":query_arg" as all queries below 
    are to be passed to the PostgreSQL driver by the 'databases' module.
    https://www.encode.io/databases/database_queries/
'''


#### CREATE EXTENSIONS ####

create_ext_pgcrypto = '''
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
'''

create_ext_citext = '''
    CREATE EXTENSION IF NOT EXISTS citext;
'''


#### CREATE DOMAINS ####

# The regex used is based on the HTML5 standard for email addresses. https://dba.stackexchange.com/questions/68266/what-is-the-best-way-to-store-an-email-address-in-postgresql
create_domain_email = '''
    CREATE DOMAIN email AS citext NOT NULL
    CHECK (
        VALUE ~ '^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    );
'''


#### DROP TABLES ####

drop_users_table = 'DROP TABLE IF EXISTS users;'


#### CREATE TABLES ####

create_users_table = '''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email_addr EMAIL UNIQUE NOT NULL,
        first_name VARCHAR(20) NOT NULL,
        last_name VARCHAR(20) NOT NULL,
        pswhash TEXT NOT NULL
    );
'''


#### INSERT RECORD ####

users_table_insert = '''
    INSERT INTO users (email_addr, first_name, last_name, pswhash)
    VALUES (:email_addr, :first_name, :last_name, crypt(:password, gen_salt('bf')));
'''


#### SELECT RECORDS ####

# USERS SELECT

users_select_all = '''
    SELECT * FROM users;
'''

users_select_limit = '''
    SELECT * FROM users LIMIT :limit;
'''

users_select_id_by_email = '''
    SELECT id FROM users WHERE email_addr = ':email_addr';
'''

# DOMAIN SELECT

domain_select_email = '''
    SELECT oid FROM pg_type WHERE typname = 'email';
'''


#### QUERY LISTS ####

create_ext_queries = [create_ext_pgcrypto, create_ext_citext]