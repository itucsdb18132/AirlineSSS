from flask import Flask, redirect, url_for, request, render_template, session, flash
import psycopg2 as dbapi2


app = Flask(__name__)
app.debug = True
app.secret_key = "secretkey123"

dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/flights/<int:code>/")
def flight(code):
    try:
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """SELECT f."FlightID", air."AirportName", air."City", x."PlaneModel" From flights as f
            inner join planes as x on x."PlaneID" = f."PlaneID"
            inner join airports as air on air."AirportID" = f."DestinationID"
            WHERE f."FlightID" = %d
        """ % code
        cursor.execute(statement)
        row = cursor.fetchall()
        return render_template('flights.html', flights = row)
    except dbapi2.DatabaseError:
        connection.rollback()
        return "Hata!"
    finally:
        connection.close()


@app.route("/flights/")
def flights():
    try:
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """SELECT f."FlightID", air."AirportName", air."City", x."PlaneModel" From flights as f
            inner join planes as x on x."PlaneID" = f."PlaneID"
            inner join airports as air on air."AirportID" = f."DestinationID"
        """
        cursor.execute(statement)
        rows = cursor.fetchall()
        return render_template('flights.html', flights=rows)
    except dbapi2.DatabaseError:
        connection.rollback()
        return "Hata!"
    finally:
        connection.close()

@app.route("/login", methods = ['POST'])
def login():
    _Username = request.form['username']
    _Password = request.form['password']
    try:
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """SELECT * FROM users WHERE username = '%s'
        """ % _Username
        cursor.execute(statement)
        password = cursor.fetchone()[1]
        if password == _Password:
            session['online'] = 1
            session['Username'] = _Username
            return redirect(url_for('userpage'))
        else:
            return render_template('errorpage.html', message = 'Wrong username/password!')
    except dbapi2.DatabaseError:
        connection.rollback()
        return "Hata!"
    finally:
        connection.close()

@app.route("/register", methods = ['POST'])
def register():
    _Username = request.form['username']
    _Password = request.form['password']
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """SELECT * FROM users WHERE username = '%s'
    """ % _Username
    cursor.execute(statement)
    if cursor.rowcount > 0:
        return render_template('errorpage.html', message= 'This username already exists!')

    statement = """INSERT INTO users (username, "password") VALUES (%s, %s)
    """
    cursor.execute(statement, (_Username, _Password))
    connection.commit()
    session['online'] = 1
    session['Username'] = _Username
    return redirect(url_for('userpage'))

@app.route("/userpage/")
def userpage():
    if 'online' in session:
        return render_template('userpage.html', username = session['Username'])
    else:
        return render_template('errorpage.html', message = 'Not Authorized!')

@app.route("/logout")
def logout():
    if session['online'] == 1:
        session.clear()
        return redirect(url_for('index'))
    else:
        return  render_template('errorpage.html', message = 'You need to log in first!')

if __name__ == "__main__":
    app.run()
