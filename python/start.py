import os
from pymongo import MongoClient, cursor
import traceback
import pymongo
client = None
import json
interarc_db = None
interarc_results = None
from flask import Flask, render_template_string, request, jsonify, render_template
app = Flask(__name__, static_url_path='/static')

__author__ = 'raviranjan'

@app.route('/')
def index():
    message = "Hello, World"
    #return render_template('index.html')
    return render_template_string('''
         <title>Ravi Ranjan</title>
         <h2>You are accessing domain over https </h2>
         <p>Secure site creation inprogress </p>
        <p> Kindly use http  <a href="http://www.ranjanravi.com"> www.ranjanravi.com</a></p>
         ''')

if __name__ == "__main__":
    if 'SERVER_PORT' in os.environ:
        server_port = int(os.environ['SERVER_PORT'])
    else:
        server_port = 443
    app.run('0.0.0.0', port=server_port, ssl_context='adhoc', debug=True)

    if 'DB_PORT' in os.environ:
        db_port = int(os.environ['DB_PORT'])
    else:
        db_port = 8082
    client = MongoClient('10.198.10.70:%s' % db_port)
    # creating connections for communicating with Mongo DB
    interarc_db = client['EmployeeData']
    interarc_results = interarc_db['results']


#@app.route('/main')
def main():
    _id = insert('339591', 'Ravi Ranjan', '28', 'india')
    print _id
    get()
    update('339591', 'Ravi Ranjan', '29', 'india')
    # delete('339591')


@app.route('/insert', methods=['POST'])
def insert():
    content_type = request.headers.get('Content-Type')
    app.logger.debug('Content-Type %s', content_type)
    data = {}
    if content_type == 'application/json':
        data = request.json
    else:
        data = request.form.to_dict()
    app.logger.debug('POST emp data: %s' % data)
    mongo_id = None
    try:
        insert = interarc_results.insert_one(data)
        mongo_id = str(insert.inserted_id)
    except (pymongo.errors.AutoReconnect,
            pymongo.errors.NotMasterError,
            pymongo.errors.ConnectionFailure,
            pymongo.errors.CollectionInvalid,
            pymongo.errors.NetworkTimeout,
            pymongo.errors.ServerSelectionTimeoutError) as ex:
        log_exception(ex)
    return json.dumps({'id': mongo_id})


@app.route('/read')
def get(emp_id):
    app.logger.debug('GET emp_id: %s' % emp_id)
    try:
        values = cursor.Cursor(interarc_results, {'emp_id':
                                                      emp_id}, limit=5) \
            .sort('interopTestDate', pymongo.DESCENDING)
    except:
        return not_found()
    data = list()
    for val in values:
        val['_id'] = str(val['_id'])
        # val.pop('_id')
        data.append(val)
    return json.dumps(data)


@app.route('/update')
def update(criteria, name, age, country):
    # Function to update record to mongo db
    try:
        interarc_db.Employees.update_one(
            {"id": criteria},
            {
                "$set": {
                    "name": name,
                    "age": age,
                    "country": country
                }
            }
        )
        print "\nRecords updated successfully\n"
    except Exception, e:
        print str(e)


@app.route('/delete')
def delete(criteria):
    # Function to delete record from mongo db
    try:
        interarc_db.Employees.delete_many({"id":criteria})
        print '\nDeletion successful\n'
    except Exception, e:
        print str(e)


def log_exception(exception):
    app.logger.error('Exception: %s Trace: %s' % (exception,
                                                  traceback.format_exc()))


@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    response = jsonify(message)
    response.status_code = 404
    return response
