import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema-sqlite.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


def new_record(conn: sqlite3.Connection, currency: str, amount: float,
               description: str = None) -> int:
    """
    Add a new record of the most recent payment, set time of payment
    initialisation
    """
    sql = """ INSERT INTO payments(currency, amount, description)
              VALUES(?,?,?)
              RETURNING id
    """
    cur = conn.cursor()
    cur.execute(sql, [currency, amount, description])
    # Retrieve id from returning query
    record = cur.fetchone()
    # Commit changes
    cur.execute("commit")
    return record['id']


def update_record(conn: sqlite3.Connection, record_id: int, hash: str):
    """
    Update payment time to make it closer to the payment broker's time,
    add hash
    """
    cur = conn.cursor()
    cur.execute(
        "UPDATE payments SET created=CURRENT_TIMESTAMP, hash=? WHERE id=?",
        [hash, record_id])
    cur.execute("commit")
