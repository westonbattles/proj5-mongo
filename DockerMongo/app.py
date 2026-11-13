import os
from flask import Flask, redirect, url_for, request, render_template, jsonify
from pymongo import MongoClient
import arrow
import acp_times # brevet calculation py file

app = Flask(__name__)

client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
db = client.tododb

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return render_template('calc.html')


    """
    _items = db.tododb.find()
    items = [item for item in _items]
    return render_template('todo.html', items=items)
    """

@app.route('/new', methods=['POST'])
def new():

    print(request.form)
    return redirect(url_for('index'))

    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)

    return redirect(url_for('index'))


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    brevet_dist_km = request.args.get('brevet_dist_km', 999, type=float)
    begin_date = request.args.get('begin_date', "", type=str)
    begin_time = request.args.get('begin_time', "", type=str)
    begin_time_arrow = arrow.get(f"{begin_date} {begin_time}", 'YYYY-MM-DD HH:mm')
    print("RAW DATE:", begin_date)
    print("RAW TIME:", begin_time)
    print("PARSED TIME:", begin_time_arrow)

    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))

    open_time = acp_times.open_time(km, brevet_dist_km, begin_time_arrow.isoformat())
    close_time = acp_times.close_time(km, brevet_dist_km, begin_time_arrow.isoformat())
    result = {"open": open_time, "close": close_time}
    return jsonify(result=result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
