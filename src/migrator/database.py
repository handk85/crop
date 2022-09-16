import logging
import mariadb
import sys


def init_db(db_config: dict):
    try:
        conn = mariadb.connect(
            user=db_config["user"],
            password=db_config["password"],
            host=db_config["host"],
            port=int(db_config["port"]),
            database=db_config["database"]
        )
        # Disable auto-commit
        conn.autocommit = False
    except mariadb.Error as e:
        logging.error(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    return conn


def get_keys_for_table(cur, table_name):
    cur.execute("DESC %s;" % table_name)
    table_keys = []
    for v in cur:
        table_keys.append(v[0])
    return table_keys


def get_keys(cur):
    cur.execute("SHOW TABLES;")
    tables = []
    for v in cur:
        tables.append(v[0])
    tables = [x for x in tables]

    key_map = {}
    for table in tables:
        key_map[table] = get_keys_for_table(cur, table)
    return key_map


def insert_data(cur, table_name: str, obj: dict):
    k = obj.keys()
    v = [obj[x] for x in k]
    query = 'INSERT INTO %s (%s) VALUES (%s);' % (table_name, ", ".join(k), ", ".join(['?' for x in k]))
    try:
        cur.execute(query, v)
    except Exception as e:
        # ignoring the exception and just logging it
        print(query)
        print(v)
        logging.error(e, exc_info=True)


def get_ids_from_database(cur, table_name:str, id_field:str):
    cur.execute("SELECT %s FROM %s" % (id_field, table_name))
    return [row[0] for row in cur]

