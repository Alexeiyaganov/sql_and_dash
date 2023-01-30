from time import time
import sqlite3


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)

    return conn


def query_task(conn, flag):
    cur = conn.cursor()
    cur_time = int(time() * 1000)
    if flag == 1:
        cur.execute(
            "SELECT ROUND(AVG(history.ended_at - history.started_at)/(1000*60*60), 2) "
            "FROM history WHERE history.status = 'Open' GROUP BY substr(history.issue_key,1,1)")
    else:
        cur.execute(
            f"SELECT h.issue_key, h.status, h.started_at FROM history as h WHERE {cur_time} "
            f"BETWEEN h.started_at AND h.ended_at AND h.status NOT IN ('Closed', 'Resolved') ORDER BY h.issue_key")
    rows = cur.fetchall()
    for row in rows:
        print(row)


def main():
    database = r"test.db"

    conn = create_connection(database)
    with conn:
        print("Query first task")
        query_task(conn, 1)

        print("Query second task")
        query_task(conn, 2)

main()
