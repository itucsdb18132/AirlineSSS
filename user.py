import psycopg2 as dbapi2
from flask import redirect, url_for, request, session, flash
from general import RenderTemplate, refreshUserData, ifAdmin
from forms import formForgotPass, formRegister, formEditUser
import mailsender

dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""

#Enes
def login("/login", methods = ['POST']):
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

#Enes
def register("/register", methods = ['POST']):
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

#Enes
def userpage("/userpage"):
    if 'online' in session:
        refreshUserData()
        return RenderTemplate('userpage.html', profileActive='active')
    else:
        return redirect(url_for('errorpage', message = 'You need to log in first!'))

#Enes
def logout("/logout"):
    if session['online'] == 1:
        session.clear()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('errorpage', message = 'You need to log in first!'))

#Enes
def buycoins("/buycoins", methods = ['GET', 'POST']):
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

#Enes
def edituser("/edituser", methods = ['GET', 'POST']):
    if refreshUserData():
        form = formEditUser()
        if request.method == 'GET':
            return RenderTemplate('edituser.html', form = form, fullname=session['Fullname'], email=session['Email'])
        else:
            if form.validate_on_submit():
                newFullname = form.fullname.data
                newEmail = form.email.data
                newPassword = form.password.data
                try:
                    if newFullname == '':
                        newFullname = session['Fullname']
                    if newEmail == '':
                        newEmail = session['Email']

                    connection = dbapi2.connect(dsn)
                    cursor = connection.cursor()
                    statement = """
                        UPDATE person SET fullname = %s, emailaddress = %s WHERE username = %s
                    """
                    cursor.execute(statement, (newFullname, newEmail, session['Username']))
                    if newPassword != '':
                        statement = """
                            UPDATE users SET password = %s WHERE username = %s
                        """
                        cursor.execute(statement, (newPassword, session['Username']))
                    connection.commit()
                    flash('You have successfully updated your profile')
                    return redirect(url_for('userpage'))
                except dbapi2.DatabaseError as e:
                    connection.rollback()
                    return redirect(url_for('error_page', str(e)))
                finally:
                    connection.close()

#Enes
def forgotpassword("/forgotpassword", methods = ['GET', 'POST']):
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
