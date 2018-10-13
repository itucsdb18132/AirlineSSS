from flask import Flask, redirect, url_for, request, render_template, session, flash
import psycopg2 as dbapi2


app = Flask(__name__)
app.debug = True
app.secret_key = "secretkey123"

dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""

class User:
    def __init__(self, uname, fname, email, balance):
        self.username = uname
        self.fullname = fname
        self.email = email
        self.balance = balance


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
            statement = """SELECT * FROM person WHERE username = '%s'
            """ % _Username
            cursor.execute(statement)
            row = cursor.fetchone()
            ActiveUser = User(row[0], row[1], row[2], row[3])
            session['Fullname'] = row[1]
            session['Email'] = row[2]
            session['Role'] = row[3]
            session['Balance'] = str(row[4])
            if ifAdmin():
                return redirect(url_for('adminpage'))
            else:
                return redirect(url_for('userpage'))
        else:
            return redirect(url_for('errorpage', message = 'Wrong username/password!'))
    except dbapi2.DatabaseError:
        connection.rollback()
        return "Hata!"
    finally:
        connection.close()

@app.route("/register", methods = ['POST'])
def register():
    _Username = request.form['username']
    _Password = request.form['password']
    _Fullname = request.form['name']
    _Email    = request.form['email']
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """SELECT * FROM users WHERE username = '%s'
    """ % _Username
    cursor.execute(statement)
    if cursor.rowcount > 0:
        return redirect(url_for('errorpage', message = 'This username already exists!'))

    statement = """INSERT INTO users (username, password) VALUES (%s, %s)
    """
    cursor.execute(statement, (_Username, _Password))
    statement = """INSERT INTO person (username, fullname, emailaddress, userrole) VALUES (%s, %s, %s, %s)
    """
    cursor.execute(statement, (_Username, _Fullname, _Email, 'P'))
    connection.commit()
    session['online']   = 1
    session['Username'] = _Username
    ActiveUser = User(_Username, _Fullname, _Email, 0)
    session['Fullname'] = _Fullname
    session['Email'] = _Email
    session['Balance'] = 0
    return redirect(url_for('userpage'))

@app.route("/userpage/")
def userpage():
    if 'online' in session:
        return render_template('userpage.html')
    else:
        return redirect(url_for('errorpage', message = 'You need to log in first!'))

@app.route("/logout")
def logout():
    if session['online'] == 1:
        session.clear()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('errorpage', message = 'You need to log in first!'))

@app.route("/adminpage")
def adminpage():
    return render_template('adminpage.html')

@app.route("/adm_users")
def adm_users():
    if ifAdmin():
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            username = session['Username']
            statement = """SELECT * FROM person WHERE username <> '%s'
            """ % username
            cursor.execute(statement)
            rows = cursor.fetchall()
            return render_template('adm_users.html', userlist = rows)
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return e
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message = 'You are not authorized!'))


@app.route("/adm_users/<username>")
def updateuser(username):
    if ifAdmin():
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """SELECT * FROM person WHERE username = '%s'
            """ % username
            cursor.execute(statement)
            row = cursor.fetchone()
            return render_template('adm_updateuser.html', user = row)
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return e
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message = 'You are not authorized!'))

@app.route('/adm_updateuser/<username>', methods = ['POST'])
def adm_updateuser(username):
    if ifAdmin():
        try:
            form_dict = request.form
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()

            statement = """UPDATE person SET 
            """
            set_text = ""
            if 'fname_cb' in form_dict and form_dict['fname_cb']:
                set_text += ("fullname = '%s'" % form_dict['fullname']) + ','
            if 'mail_cb' in form_dict and form_dict['mail_cb']:
                set_text += ("emailaddress = '%s'" % form_dict['mail']) + ','
            if 'role_cb' in form_dict and form_dict['role_cb']:
                set_text += ("userrole = '%s'" % form_dict['role']) + ','
            if 'balance_cb' in form_dict and form_dict['balance_cb']:
                set_text += ("balance = '%s'" % form_dict['balance']) + ','
            if len(set_text) > 0:
                set_text = set_text[:-1]
                statement += set_text
                statement += " WHERE username = '%s'" % username
            else:
                return redirect(url_for('adm_users'))
            cursor.execute(statement)
            connection.commit()
            return redirect(url_for('adm_users'))
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return e
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message = 'You are not authorized!'))

@app.route("/adm_flights")
def adm_flights():
    if ifAdmin():
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """SELECT * FROM users WHERE username <> %s
            """
            cursor.execute(statement, str(session['Username']))
            rows = cursor.fetchall()
            return render_template('adm_users.html', userlist = rows)
        except dbapi2.DatabaseError:
            connection.rollback()
            return "Hata!"
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))

@app.route('/errorpage/<message>')
def errorpage(message):
    return  render_template('errorpage.html', message = message)

def ifAdmin():
    if 'Role' in session and session['Role'] == 'A':
        return True
    else:
        return False

if __name__ == "__main__":
    app.run()
