from typing import List, Dict
import simplejson as json
from flask import Flask, request, Response, redirect
from flask import render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

app.config['MYSQL_DATABASE_HOST'] = 'db'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_DB'] = 'zillowData'
mysql.init_app(app)


@app.route('/', methods=['GET'])
def index():
    user = {'username': 'Zillow Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblZillowImport')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, listings=result)


@app.route('/view/<int:listing_id>', methods=['GET'])
def record_view(listing_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblZillowImport WHERE id=%s', listing_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', listing=result[0])


@app.route('/edit/<int:listing_id>', methods=['GET'])
def form_edit_get(listing_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblZillowImport WHERE id=%s', listing_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', listing=result[0])


@app.route('/edit/<int:listing_id>', methods=['POST'])
def form_update_post(listing_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Index'), request.form.get('Living_Space_sq_ft'), request.form.get('Beds'),
                 request.form.get('Baths'), request.form.get('Zip'),
                 request.form.get('Year'), request.form.get('List_Price'), listing_id)
    sql_update_query = """UPDATE tblZillowImport t SET t.`Index` = %s, t.Living_Space_sq_ft = %s, t.Beds = %s, t.Baths = 
    %s, t.Zip = %s, t.Year = %s, t.List_Price = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/listings/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Listing Form')


@app.route('/listings/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Index'), request.form.get('Living_Space_sq_ft'), request.form.get('Beds'),
                 request.form.get('Baths'), request.form.get('Zip'),
                 request.form.get('Year'), request.form.get('List_Price'))
    sql_insert_query = """INSERT INTO tblZillowImport (`Index`,Living_Space_sq_ft,Beds,Baths,Zip,Year,List_Price) VALUES (%s, %s,%s, %s,%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@app.route('/delete/<int:listing_id>', methods=['POST'])
def form_delete_post(listing_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblZillowImport WHERE id = %s """
    cursor.execute(sql_delete_query, listing_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/listings', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblZillowImport')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/listings/<int:listing_id>', methods=['GET'])
def api_retrieve(listing_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM tblZillowImport WHERE id=%s', listing_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/listings/<int:listing_id>', methods=['PUT'])
def api_edit(listing_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Index'], content['Living_Space_sq_ft'], content['Beds'],
                 content['Baths'], content['Zip'],
                 content['Year'], content['List_Price'],listing_id)
    sql_update_query = """UPDATE tblZillowImport t SET t.`Index` = %s, t.Living_Space_sq_ft = %s, t.Beds = %s, t.Baths = 
        %s, t.Zip = %s, t.Year = %s, t.List_Price = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/listings', methods=['POST'])
def api_add() -> str:

    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['Index'], content['Living_Space_sq_ft'], content['Beds'],
                 content['Baths'], content['Zip'],
                 content['Year'], request.form.get('List_Price'))
    sql_insert_query = """INSERT INTO tblZillowImport (`Index`,Living_Space_sq_ft,Beds,Baths,Zip,Year,List_Price) VALUES (%s, %s,%s, %s,%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp

@app.route('/api/v1/listings/<int:listing_id>', methods=['DELETE'])
def api_delete(listing_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM tblZillowImport WHERE id = %s """
    cursor.execute(sql_delete_query, listing_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)