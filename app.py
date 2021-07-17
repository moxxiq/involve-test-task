from flask import Flask, render_template, request, redirect, url_for
from payment_processing import processing_map

app = Flask(__name__)
app.config.from_pyfile("config.py")


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
    app.run()
