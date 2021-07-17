from flask import Flask, render_template, request
from collections import OrderedDict
from hashlib import sha256
from db import get_db, new_record, update_record
from config import shop_id, SECRET_KEY


def gen_sha256(required: dict) -> str:
    """Generate sha256 hash of any [unsorted] dictionary"""
    required = OrderedDict(sorted(required.items()))
    # prepare a string for hashing
    str_to_hash = ":".join(str(v) for v in required.values()) + SECRET_KEY
    return sha256(str_to_hash.encode('utf-8')).hexdigest()


def eur(params):
    """Process payment on EUR currency"""
    # connect to DB and get order_id
    connection = get_db()
    record_id = new_record(connection,
                           params.get("currency"),
                           params.get("amount"),
                           params.get("description"),)
    # required arguments to form an sha256 hash
    required = dict(
        amount=int(float(params.get("amount")) * 100),
        currency=978,
        shop_id=shop_id,
        shop_order_id=record_id,
    )
    required_hash = gen_sha256(required)
    # the rest of the arguments including the hash
    additional = dict(
        sha256hash=required_hash,
        description=params.get("description"),
    )
    # merge two dict to one to pass to the page form
    context = required | additional
    # update record with closer time and the hash
    update_record(connection, record_id, additional["sha256hash"])
    return render_template('eur.html', **context)


def usd(params):
    pass


def rub(params):
    pass


processing_map = {
    "EUR": eur,
    "USD": usd,
    "RUB": rub,
}


