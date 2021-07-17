# import sqlite3
import psycopg2

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            dbname=current_app.config['DBNAME'],
            user=current_app.config['DBUSER'],
            password=current_app.config['DBPASS'],
            host=current_app.config['DBHOST'],
            port=current_app.config['DBPORT'],
        )
    #     g.db = sqlite3.connect(
    #         current_app.config['DATABASE'],
    #         detect_types=sqlite3.PARSE_DECLTYPES
    #     )
    #     g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    cur = db.cursor()
    with current_app.open_resource('schema-postgresql.sql') as f:
        cur.execute(f.read().decode('utf8'))
        cur.execute("commit")
    cur.close()



@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def new_record(conn, currency: str, amount: float,
               description: str = None) -> int:
    """
    Add a new record of the most recent payment, set time of payment
    initialisation
    """
    sql = """ INSERT INTO payments(currency, amount, description)
              VALUES(%s, %s, %s)
              RETURNING id
    """
    cur = conn.cursor()
    cur.execute(sql, [currency, amount, description])
    # Retrieve id from returning query
    record = tuple(cur.fetchone())
    # Commit changes
    cur.execute("commit")
    cur.close()
    return record[0]


def update_record(conn, record_id: int, hash: str):
    """
    Update payment time to make it closer to the payment broker's time,
    add hash
    """
    cur = conn.cursor()
    cur.execute(
        "UPDATE payments SET created=CURRENT_TIMESTAMP, hash=%s WHERE id=%s",
        [hash, record_id])
    cur.execute("commit")
    cur.close()
