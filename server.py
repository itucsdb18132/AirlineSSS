import os
from flask import Flask, redirect, url_for, request, render_template, session, flash, send_from_directory
import psycopg2 as dbapi2
import datetime
import mailsender
import decimal
from forms import formSendPost, formForgotPass, formRegister, formLogin
from werkzeug.utils import secure_filename
from base64 import b64encode, b64decode

app = Flask(__name__)
app.debug = True
app.secret_key = "secretkey123"
WTF_CSRF_SECRET_KEY = 'secretkey123'



dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""

##--------------------SERCAN YETKIN-------------------------------------------------##
@app.route('/')
def index():
    refreshUserData()
    _Datetime = datetime.datetime.now()
    date = _Datetime.strftime("%Y-%m-%d")
    try:
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """SELECT city FROM cities
                        ORDER BY city
                    """
        cursor.execute(statement)
        cities = cursor.fetchall()

        statement = """SELECT postid, fullname, content, date, title, img.data, img.filename FROM posts
                        INNER JOIN person ON poster = username
                        LEFT OUTER JOIN uploads as img ON posts.image = img.id
                        ORDER BY postid DESC
                        LIMIT 6
                    """
        cursor.execute(statement)
        posts = cursor.fetchall()
        images = {}
        for post in posts:
            images[post[0]] = b64encode(post[5]).decode('utf-8')
        return RenderTemplate('index.html', cities=cities, date=date, homeActive='active', posts=posts, images=images)
    except dbapi2.DatabaseError as e:
        connection.rollback()
        return str(e)
    finally:
        connection.close()

@app.route('/searchList', methods=['GET', 'POST'])
def searchList():
    departure = request.form['from']
    destination = request.form['to']
    departure_time = request.form['date']
    try:
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """SELECT f.flight_id,a.airport_name, c.city, a2.airport_name, c2.city, p.plane_model, f.departure_time, f.arrival_time FROM flights AS f 
                                    INNER JOIN airports AS a ON f.departure_id = a.airport_id
                                    INNER JOIN airports AS a2 ON f.destination_id = a2.airport_id
                                    INNER JOIN planes AS p ON f.plane_id = p.plane_id
                                    INNER JOIN cities AS c ON a.city_id = c.city_id
                                    INNER JOIN cities AS c2 ON a2.city_id = c2.city_id
                                    WHERE c.city = %s AND c2.city = %s AND f.departure_time::text LIKE %s"""
        departure_time += '%'
        cursor.execute(statement, (departure, destination, departure_time))
        rows = cursor.fetchall()

        return RenderTemplate('flights.html', flights=rows, flightsActive='active')
    except dbapi2.DatabaseError as e:
        connection.rollback()
        return str(e)
    finally:
        connection.close()

@app.route("/flights")
def flights():

        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """SELECT f.flight_id,a.airport_name, c.city, a2.airport_name, c2.city, p.plane_model, f.departure_time, f.arrival_time FROM flights AS f 
                            INNER JOIN airports AS a ON f.departure_id = a.airport_id
                            INNER JOIN airports AS a2 ON f.destination_id = a2.airport_id
                            INNER JOIN planes AS p ON f.plane_id = p.plane_id
                            INNER JOIN cities AS c ON a.city_id = c.city_id
                            INNER JOIN cities AS c2 ON a2.city_id = c2.city_id
                        """
            cursor.execute(statement)
            rows = cursor.fetchall()

            return RenderTemplate('flights.html', flights=rows, flightsActive='active')
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return str(e)
        finally:
            connection.close()

@app.route('/adm_updateflight', methods = ['GET', 'POST'])
def adm_updateflight():
    refreshUserData()
    if ifAdmin():
        if request.method == 'GET' :
            try:
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """ SELECT airport_name, city, airport_id FROM airports AS a
                INNER JOIN cities AS c ON a.city_id = c.city_id
                                    ORDER BY city
                """
                cursor.execute(statement)
                rows = cursor.fetchall()
                statement = """ SELECT plane_id, plane_model, bsn_capacity, eco_capacity FROM planes AS p
                                ORDER BY plane_id
                """
                cursor.execute(statement)
                plane = cursor.fetchall()
                return RenderTemplate('adm_updateflight.html', cities=rows, planes=plane, adminActive='active')
            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata1!"
            finally:
                connection.close()
        else :
            try:
                _from = request.form['from']
                _to = request.form['to']
                _on = request.form['on']
                _arr_date = request.form['arr_date']
                _dep_date = request.form['dep_date']
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """ INSERT INTO flights (destination_id, plane_id, departure_time, arrival_time, departure_id)
                                            VALUES (%s, %s,%s,%s,%s)
                                    """
                cursor.execute(statement, (_to, _on, _dep_date, _arr_date, _from))
                connection.commit()
                statement = """ SELECT MAX(flight_id) FROM flights
                                                    """
                cursor.execute(statement)
                flight = cursor.fetchone()
                create_tickets(flight, 100)
                return RenderTemplate('adm_updateflight.html', adminActive='active')
            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata2!"
            finally:
                connection.close()


    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))

##--------------------SERCAN YETKIN-------------------------------------------------##



##--------------------SELIM ENES KILICASLAN-----------------------------------------##

@app.route('/test/<id>')
def test(id):
    connection = dbapi2.connect(dsn)
    cursor = connection.cursor()
    statement = """SELECT data FROM uploads WHERE id=%s
    """ % id
    cursor.execute(statement)
    data = cursor.fetchone()
    return str(data[0])

def RenderTemplate(template, **context):
    context['registerForm'] = formRegister()
    return render_template(template, **context)

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
    form = formRegister()
    _Username = form.username.data
    _Password = form.password.data
    _Fullname = form.name.data
    _Email    = form.email.data
    if form.validate_on_submit():
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
    for error in form.errors:
        flash(form.errors[error][0])
    return redirect(url_for('index'))

@app.route("/userpage/")
def userpage():
    if 'online' in session:
        refreshUserData()
        return RenderTemplate('userpage.html', profileActive='active')
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
        return RenderTemplate('adminpage.html', adminActive='active')
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
            return RenderTemplate('adm_users.html', userlist = rows, adminActive='active')
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
            return RenderTemplate('adm_updateuser.html', user = row, adminActive='active')
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

@app.route('/errorpage/<message>')
def errorpage(message):
    return  RenderTemplate('errorpage.html', message = message)

@app.route('/about')
def about():
    return RenderTemplate('about.html', aboutActive='active')

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
            return RenderTemplate('adm_users.html', adminActive='active')
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
    statement = """SELECT p.postid, f.fullname, p.content, p.date, p.time, f.userrole, p.title, img.filename, img.data FROM posts as p
                LEFT OUTER JOIN person as f ON f.username = p.poster
                LEFT OUTER JOIN uploads as img ON p.image = img.id 
                ORDER BY p.postid DESC
    """
    cursor.execute(statement)
    posts = cursor.fetchall()
    images = {}
    for post in posts:
        images[post[0]] = b64encode(post[8]).decode('utf-8')
    return RenderTemplate('news.html', posts = posts, newsActive='active', images = images)

@app.route('/sendpost', methods = ['post'])
def sendpost():
    refreshUserData()
    if ifAdmin():
        form = formSendPost()
        if form.validate_on_submit():

            image = form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join('./static/img/uploads', filename))

            _Datetime = datetime.datetime.now()
            poster = session['Username']
            content = form.content.data
            title = form.title.data
            date = _Datetime.strftime("%d/%m/%Y")
            time = _Datetime.strftime("%H:%M")
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """INSERT INTO posts (poster, content, date, time, title, image) VALUES (%s, %s, TO_DATE(%s, 'DD/MM/YYYY'), %s, %s, %s)
                        """
            cursor.execute(statement, (poster, content, date, time, title, filename))
            connection.commit()
            flash('You have succesfully posted an entry.')
            return redirect(url_for('test'))
        for key in form.errors:
            flash(form.errors[key][0])

    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))
    return redirect(url_for('news'))

@app.route('/adm_sendpost', methods = ['GET', 'POST'])
def adm_sendpost():
    refreshUserData()
    if ifAdmin():
        form = formSendPost()
        if(request.method == 'POST'):
            if form.validate_on_submit():
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                image = form.image.data
                filename = secure_filename(image.filename)
                statement = """INSERT INTO uploads (filename, data) VALUES (%s, %s)
                            """
                cursor.execute(statement, (filename, dbapi2.Binary(image.read())))
                connection.commit()
                statement = """SELECT MAX(id) FROM uploads
                            """
                cursor.execute(statement, (filename, dbapi2.Binary(image.read())))
                id = cursor.fetchone()
                _Datetime = datetime.datetime.now()
                poster = session['Username']
                content = form.content.data
                title = form.title.data
                date = _Datetime.strftime("%d/%m/%Y")
                time = _Datetime.strftime("%H:%M")
                statement = """INSERT INTO posts (poster, content, date, time, title, image) VALUES (%s, %s, TO_DATE(%s, 'DD/MM/YYYY'), %s, %s, %s)
                            """
                cursor.execute(statement, (poster, content, date, time, title, id))
                connection.commit()
                flash('You have succesfully posted an entry.')
                return redirect(url_for('news'))
            for key in form.errors:
                flash(form.errors[key][0])

        return RenderTemplate('adm_sendpost.html', adminActive='active', form=form)
    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))


@app.route('/buycoins', methods=['GET', 'POST'])
def buycoins():
    if request.method == 'GET':
        return RenderTemplate('buycoins.html', coinActive='active')
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
                return RenderTemplate('adm_pymreqs.html', payments = payments, adminActive='active')
            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata!"
            finally:
                connection.close()
            return RenderTemplate('adm_pymreqs.html', adminActive='active')
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
    form = formForgotPass()
    refreshUserData()
    if 'Username' in session:
        return redirect(url_for('errorpage'), message = 'Not allowed!')
    if request.method == 'GET':
        return RenderTemplate('forgotpassword.html', form=form)
    else:
        if form.validate_on_submit():
            username = form.username.data
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
                    return RenderTemplate('forgotpassword.html', form=form)
                else:
                    flash('This username is not registered to our website!')
                    return RenderTemplate('forgotpassword.html', form=form)
            except dbapi2.DatabaseError as e:
                connection.rollback()
                return str(e)
            finally:
                connection.close()
        for error in form.errors:
            flash(form.errors[error][0])
        return RenderTemplate('forgotpassword.html', form=form)

##--------------------SELIM ENES KILICASLAN-----------------------------------------##




##--------------------MUHAMMED SAID DIKICI------------------------------------------##

@app.route('/buy_ticket/<int:flight_id>', methods = ['GET', 'POST'])
def buy_ticket(flight_id):
    if 'Username' in session:
        refreshUserData()
        if request.method == 'GET':
            try:
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """SELECT class, COUNT(*) FROM tickets WHERE flight_id = '%s' AND username IS NULL 
                                    GROUP BY class
                            
                """ % flight_id
                cursor.execute(statement)
                rows = cursor.fetchall()
                emptyseatsforeco = 0
                emptyseatsforbsn = 0
                for row in rows:
                    if row[0] == 'E':
                        emptyseatsforeco = row[1]
                    elif row[0] == 'B':
                        emptyseatsforbsn = row[1]

                statement = """SELECT class, MIN(price) FROM tickets WHERE flight_id = '%s' AND username IS NULL 
                                                    GROUP BY class

                                """ % flight_id
                cursor.execute(statement)
                rows = cursor.fetchall()
                priceforeco = 0
                priceforbsn = 0
                for row in rows:
                    if row[0] == 'E':
                        priceforeco = row[1]
                    elif row[0] == 'B':
                        priceforbsn = row[1]

                return RenderTemplate('buy_ticket.html', flightid = flight_id, balance = session['Balance'], emptyseatsforeco = emptyseatsforeco, emptyseatsforbsn =emptyseatsforbsn, priceforeco = priceforeco, priceforbsn = priceforbsn, flightsActive='active')
            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata!"
            finally:
                connection.close()
        elif request.method == 'POST':
            try:
                classtype = request.form['class']
                session['Username']
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """SELECT ticket_id, price from tickets 
                                    WHERE ticket_id = (SELECT MIN(ticket_id)
                                        FROM tickets WHERE flight_id = %s AND username IS NULL AND class = %s)
                                            AND flight_id = %s
                  """
                cursor.execute(statement, (flight_id, classtype, flight_id))
                row = cursor.fetchone()
                ticketid = row[0]
                ticketprice = row[1]
                if ticketprice <= decimal.Decimal(session['Balance']):
                    statement = """UPDATE tickets 
                                        SET username = %s
                                            WHERE ticket_id = %s
                                                AND flight_id = %s
                                                
                    
                                    """
                    cursor.execute(statement, (session['Username'], ticketid, flight_id))
                    statement = """UPDATE person 
                                        SET balance = balance-%s
                                            WHERE username = %s
    
    
                                    """
                    cursor.execute(statement,(ticketprice, session['Username']))
                    connection.commit()
                    refreshUserData()
                    flash('Ticket has been bought successfully. Your new balance is %s SCoins' % session['Balance'])

                    return redirect(url_for('index'))
                else:
                    flash('Your balance is not enough!')
                    return redirect(url_for('buycoins'))

            except dbapi2.DatabaseError as e:
                connection.rollback()
                return str(e)
            finally:
                connection.close()
    else:
        return redirect(url_for('errorpage', message = 'Please log in first'))


def create_tickets(flight_id, eco_first_ticket_price):
    ecoticketid = 1
    bsnticketid = 1
    bsnprice = eco_first_ticket_price * 2
    refreshUserData()
    if ifAdmin():
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()

            connection.commit()
            statement = """SELECT bsn_capacity, eco_capacity FROM flights 
            INNER JOIN planes ON planes.plane_id = flights.plane_id
            WHERE flight_id ='%s'
            """
            cursor.execute(statement, (flight_id))
            capacities = cursor.fetchone()
            bsn_capacity = capacities[0]
            eco_capacity = capacities[1]

            for i in range(bsn_capacity):
                statement = """INSERT INTO tickets(flight_id, ticket_id, price, class) VALUES(%s, %s, %s, 'B')
                """

                cursor.execute(statement, (flight_id, bsnticketid, bsnprice))
                bsnticketid += 1
                bsnprice += 10
            ecoticketid = bsn_capacity + 1
            for i in range(eco_capacity):
                statement = """INSERT INTO tickets(flight_id, ticket_id, price, class) VALUES(%s, %s, %s, 'E')
                """

                cursor.execute(statement, (flight_id, ecoticketid, eco_first_ticket_price))
                ecoticketid += 1
                eco_first_ticket_price += 5
            connection.commit()
        except dbapi2.DatabaseError as e:
            connection.rollback()
            return redirect(url_for('errorpage', message="Create Tickets Fonksiyonunda Hata!"))
        finally:
            connection.close()

##--------------------MUHAMMED SAID DIKICI------------------------------------------##

if __name__ == "__main__":
    app.run()
