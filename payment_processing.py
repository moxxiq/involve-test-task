from flask import Flask, render_template, request
from collections import OrderedDict
from hashlib import sha256


def eur(params):
    """Process payment on EUR currency"""
    # TODO: connect to DB and get order_id
    # required arguments to form an sha256 hash
    required = OrderedDict(sorted(dict(
        amount=params.get("amount"),
        currency=978,
        shop_id=5,
        shop_order_id=None,
    ).items()))
    # the rest of the arguments including the hash
    additional = dict(
        sha256hash=sha256(required.values())
    )
    # merge two dict to one to pass to the page form
    context = required | additional
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


