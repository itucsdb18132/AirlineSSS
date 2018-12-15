import psycopg2 as dbapi2
from flask import render_template, session
import datetime
from base64 import b64encode
from forms import formRegister

dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""

#Enes
def RenderTemplate(template, **context):
    context['registerForm'] = formRegister()
    return render_template(template, **context)

@app.route('/errorpage/<message>')
def errorpage(message):
    return  RenderTemplate('errorpage.html', message = message)

#Enes
@app.route('/about')
def about():
    return RenderTemplate('about.html', aboutActive='active')

#Enes
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

#Enes
def ifAdmin():
    if 'Username' in session:
        _Refreshed = refreshUserData()
        if _Refreshed:
            if session['Role'] == 'A':
                return True
        else:
            return _Refreshed
    return False

#Enes
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


