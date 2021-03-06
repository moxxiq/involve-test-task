from flask import render_template, redirect
from collections import OrderedDict
from hashlib import sha256
from db import get_db, new_record, update_record
from config import shop_id, SECRET_KEY, payway
import requests
import json


def gen_sha256(required: dict) -> str:
    """Generate sha256 hash of any [unsorted] dictionary"""
    required = OrderedDict(sorted(required.items()))
    # prepare a string for hashing
    str_to_hash = ":".join(str(v) for v in required.values()) + SECRET_KEY
    return sha256(str_to_hash.encode('utf-8')).hexdigest()


def make_db_record(params: dict) -> int:
    """ Connect to DB and get order_id """
    connection = get_db()
    return new_record(connection,
                      params.get("currency"),
                      int(float(params.get("amount")) * 100),
                      params.get("description"), )


def update_time_hash(record_id: int, sha256hash: str):
    """ Update record with closer time and the hash """
    connection = get_db()
    update_record(connection, record_id, sha256hash)


def eur(params):
    """Process payment on EUR currency"""
    record_id = make_db_record(params)
    # required arguments to form an sha256 hash
    required = dict(
        amount=float(params.get("amount")),
        currency=978,
        shop_id=shop_id,
        shop_order_id=record_id,
    )
    # the rest of the arguments including the hash
    additional = dict(
        sign=gen_sha256(required),
        description=params.get("description"),
    )
    # merge two dict to one to pass to the page form
    context = required | additional
    update_time_hash(record_id, additional["sign"])
    return render_template('eur.html', **context)


def usd(params):
    """Process payment on EUR currency"""
    record_id = make_db_record(params)
    required = dict(
        shop_amount=float(params.get("amount")),
        shop_currency=840,
        shop_id=shop_id,
        shop_order_id=record_id,
        payer_currency=980
    )
    additional = dict(
        sign=gen_sha256(required),
        description=params.get("description"),
    )
    context = required | additional
    update_time_hash(record_id, additional["sign"])
    response = requests.post(
        "https://core.piastrix.com/bill/create",
        data=json.dumps(context),
        headers={"Content-type": "application/json"},
    ).json()
    if not response.get("data"):
        return response.get("message")
    return redirect(response["data"]["url"])


def rub(params):
    """Process payment on RUB currency"""
    record_id = make_db_record(params)
    required = dict(
        amount=float(params.get("amount")),
        currency=643,
        shop_id=shop_id,
        shop_order_id=record_id,
        payway=payway,
    )
    additional = dict(
        sign=gen_sha256(required),
        description=params.get("description"),
    )
    context = required | additional
    update_time_hash(record_id, additional["sign"])
    response = requests.post(
        "https://core.piastrix.com/invoice/create",
        data=json.dumps(context),
        headers={"Content-type": "application/json"},
    ).json()
    if not response.get("data"):
        return response.get("message")
    # merge context to show user confirmation with necessary data
    data = response["data"] | context
    return render_template('rub.html', **data)


processing_map = {
    "EUR": eur,
    "USD": usd,
    "RUB": rub,
}


