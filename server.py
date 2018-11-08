from flask import Flask, redirect, url_for, request, render_template, session, flash
import psycopg2 as dbapi2
import datetime
import mailsender


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
    refreshUserData()
    return render_template('index.html')

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
        if cursor.rowcount > 0:
            password = cursor.fetchone()[1]
            if password == _Password:
                session['online'] = 1
                session['Username'] = _Username
                statement = """SELECT * FROM person WHERE username = '%s'
                """ % _Username
                cursor.execute(statement)
                row = cursor.fetchone()
                session['Fullname'] = row[1]
                session['Email'] = row[2]
                session['Role'] = row[3]
                session['Balance'] = str(row[4])
                if ifAdmin():
                    return redirect(url_for('adminpage'))
                else:
                    return redirect(url_for('userpage'))
        return redirect(url_for('errorpage', message = 'Wrong username or password!'))
    except dbapi2.DatabaseError as e:
        connection.rollback()
        return str(e)
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
    session['Fullname'] = _Fullname
    session['Email'] = _Email
    session['Balance'] = 0
    flash('You have been succesfully registered.')
    return redirect(url_for('userpage'))

@app.route("/userpage/")
def userpage():
    if 'online' in session:
        refreshUserData()
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
    if ifAdmin():
        return render_template('adminpage.html')
    else:
        return redirect(url_for('errorpage', message = 'You are not authorized!'))

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
            flash('You have succesfully updated a user.')
            return redirect(url_for('adm_users'))
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return e
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message = 'You are not authorized!'))

@app.route("/flights")
def flights():

        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """SELECT f.flight_id,a.airport_name, a.city, p.plane_model, f.departure_time, f.landing_time FROM flights AS f 
                            INNER JOIN airports AS a ON f.destination_id = a.airport_id
                            INNER JOIN planes AS p ON f.plane_id = p.plane_id
                        """
            cursor.execute(statement)
            rows = cursor.fetchall()

            return render_template('flights.html', flights=rows)
        except dbapi2.DatabaseError:
            connection.rollback()
            return "Hata!"
        finally:
            connection.close()


@app.route('/adm_updateflight/<flight_id>', methods = ['GET', 'POST'])
def adm_updateflight():
    if ifAdmin():
        if request.method == 'POST' :
            try:
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """UPDATE flights SET
                """
                cursor.execute(statement)
                rows = cursor.fetchall()
                return render_template('adm_updateflight.html', flight=rows)
            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata!"
            finally:
                connection.close()
        else:
            return render_template('adm_updateflight.html')

    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))

@app.route('/errorpage/<message>')
def errorpage(message):
    return  render_template('errorpage.html', message = message)

@app.route('/about')
def about():
    return render_template('about.html')

def ifAdmin():
    if 'Username' in session:
        _Refreshed = refreshUserData()
        if _Refreshed:
            if session['Role'] == 'A':
                return True
        else:
            return _Refreshed
    return False

def refreshUserData():
    if 'Username' in session:
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """SELECT * FROM person WHERE username = '%s'
            """ % session['Username']
            cursor.execute(statement)
            row = cursor.fetchone()
            session['Fullname'] = row[1]
            session['Email'] = row[2]
            session['Role'] = row[3]
            session['Balance'] = str(row[4])
            return True
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return e
        finally:
            connection.close()
    else:
        return False

@app.route('/deleteuser/<username>', methods=['post'])
def deleteuser(username):
    if ifAdmin():
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """DELETE FROM users WHERE username = '%s'
            """ % username
            cursor.execute(statement)
            statement = """DELETE FROM person WHERE username = '%s'
            """ % username
            cursor.execute(statement)
            connection.commit()
            flash('You have succesfully deleted a user.')
            return render_template('adm_users.html')
        except dbapi2.DatabaseError:
            connection.rollback()
            return "Hata!"
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))

@app.route('/news')
def news():
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """SELECT p.postid, f.fullname, p.poster, p.content, p.date, p.time, f.userrole FROM posts as p
                LEFT OUTER JOIN person as f ON f.username = p.poster 
                ORDER BY p.postid DESC
    """
    cursor.execute(statement)
    posts = cursor.fetchall()
    return render_template('news.html', posts = posts)

@app.route('/sendpost', methods = ['post'])
def sendpost():
    refreshUserData()
    if ifAdmin():
        _Datetime = datetime.datetime.now()
        poster = session['Username']
        content = request.form['content']
        date = _Datetime.strftime("%d/%m/%Y")
        time = _Datetime.strftime("%H:%M")
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """INSERT INTO posts (poster, content, date, time) VALUES (%s, %s, TO_DATE(%s, 'DD/MM/YYYY'), %s)
        """
        cursor.execute(statement, (poster, content, date, time))
        connection.commit()
        flash('You have succesfully posted an entry.')
    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))
    return redirect(url_for('news'))

@app.route('/adm_sendpost')
def adm_sendpost():
    refreshUserData()
    if ifAdmin():
        return render_template('adm_sendpost.html')
    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))

@app.route('/buycoins', methods=['GET', 'POST'])
def buycoins():
    if request.method == 'GET':
        return render_template('buycoins.html')
    elif request.method == 'POST':
        amount = request.form['amount']
        refreshUserData()
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """INSERT INTO payments(username, amount) VALUES(%s, %s)
            """
            cursor.execute(statement, (session['Username'], amount))
            connection.commit()
            flash('Payment request has been sent to admins.')
            return redirect(url_for('userpage'))
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return str(e)
        finally:
            connection.close()

@app.route('/adm_pymreqs', methods=['GET','POST'])
def adm_pymreqs():
    refreshUserData()
    if ifAdmin():
        if request.method == 'GET':
            try:
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """SELECT paymentid, username, amount FROM payments WHERE approved = '0'
                                ORDER BY paymentid ASC
                """
                cursor.execute(statement)
                payments = cursor.fetchall()
                return render_template('adm_pymreqs.html', payments = payments)
            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata!"
            finally:
                connection.close()
            return render_template('adm_pymreqs.html')
        elif request.method == 'POST':
            try:
                for key in request.form.keys():
                    pymId = key[3:]
                    if request.form[key]:

                        connection = dbapi2.connect(dsn)
                        cursor = connection.cursor()
                        statement = """UPDATE payments SET approved = %s, approved_by = %s WHERE paymentid = %s
                        """
                        cursor.execute(statement, ('1', session['Username'], pymId))

                        ##statement = """SELECT amount FROM payments WHERE paymentid = %s
                        ##"""
                        ##cursor.execute(statement, (pymId))
                        ##amount = cursor.fetchone()

                        statement = """UPDATE person
                                        SET balance = t1.balance + t2.amount
                                        FROM person as t1
                                        INNER JOIN payments as t2 ON t2.username = t1.username 
                                        WHERE t2.paymentid = %s
                                          AND person.username = t2.username;
                        """ % pymId
                        cursor.execute(statement)
                        connection.commit()
                flash('Approved requests')
                return redirect(url_for('adm_pymreqs'))
            except dbapi2.DatabaseError as e:
                connection.rollback()
                return str(e)
            finally:
                connection.close()

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    refreshUserData()
    if 'Username' in session:
        return redirect(url_for('errorpage'), message = 'Not allowed!')
    if request.method == 'GET':
        return render_template('forgotpassword.html')
    else:
        username = request.form['username']
        refreshUserData()
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """SELECT p.emailaddress, u.password FROM person AS p
                                INNER JOIN users AS u ON u.username = p.username
                                WHERE p.username = '%s'
            """ % username
            cursor.execute(statement)
            row = cursor.fetchone()
            if row:
                mailsender.sendMail(row[1], row[0])
                flash('Your password has been sent to your email address. Please check your inbox.')
                return redirect(url_for('forgotpassword'))
            else:
                flash('This username is not registered to our website!')
                return redirect(url_for('forgotpassword'))
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return str(e)
        finally:
            connection.close()


if __name__ == "__main__":
    app.run()
