from flask import Flask, render_template, request, redirect, url_for, current_app
from payment_processing import processing_map
import db
import os

app = Flask(__name__)
app.config.from_pyfile("config.py")
app.teardown_appcontext(db.close_db)
app.cli.add_command(db.init_db_command)


@app.route('/')
def index_form():
    """Show the form to the users"""
    return render_template('index.html')


@app.route('/', methods=['POST'])
def process_payment():
    """Lead payment to processing"""
    if request.form:
        return processing_map[request.form.get("currency")](request.form)
    return redirect(url_for('/'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ['PORT'])
