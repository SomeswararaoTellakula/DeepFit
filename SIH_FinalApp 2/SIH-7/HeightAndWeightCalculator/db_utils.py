# db_utils.py
from db_config import connect_mongodb
from error_logger import log_error

def get_db():
    global client, db, mongodb_connected
    try:
        if 'db' in globals() and db is not None:
            return db
    except NameError:
        pass
    try:
        client_conn, db_conn = connect_mongodb()
        if db_conn is not None:
            globals()['client'] = client_conn
            globals()['db'] = db_conn
            globals()['mongodb_connected'] = True
            return db_conn
    except Exception as e:
        try:
            log_error(f"get_db error: {e}")
        except Exception:
            print(f"get_db error: {e}")
    return None
