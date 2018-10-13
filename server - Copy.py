from flask import Flask, redirect, url_for, request, render_template

import psycopg2 as dbapi2
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
##app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ddzwibxvysqwgx:9e0edae8756536ffdba78314ebde69e2d019e58a2c05dfbad508b5eb657ac9e7@ec2-54-247-101-205.eu-west-1.compute.amazonaws.com:5432/d8o6dthnk5anke'
##app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:itucspw@localhost:65530/itucsdb'
app.debug = True
##db = SQLAlchemy(app)


dsn = """user='ddzwibxvysqwgx' password='9e0edae8756536ffdba78314ebde69e2d019e58a2c05dfbad508b5eb657ac9e7'
         host='ec2-54-247-101-205.eu-west-1.compute.amazonaws.com' port=5432 dbname='d8o6dthnk5anke'"""

_Dictionary = {
    "SelimK" : "aslan123",
    "admin"  : "admin"
}

class Users(db.Model):
    Username = db.Column(db.String(20), primary_key = True)
    Password = db.Column(db.String(20))

    def __init__(self, _Username, _Password):
        self.Username = _Username
        self.Password = _Password

    def __repr__(self):
        return '<Kullanici Adi: %s>' % self.Username

@app.route("/")
def index():
    
    return render_template('main.html')

@app.route("/main", methods = ['GET', 'POST'])
def main():
    if request.method == 'POST':
        userName = request.form['nm']
        userPass = request.form['pw']
        _User = Users.query.filter_by( Username = userName ).first()
      ##  if _User.count() == 1:
        if userPass == _User.Password:
            return redirect(url_for('redirectUser', name = userName))
        return "Hatali Kullanici Adi/Sifre"
    else:
        userName = request.args.get('nm')
        return redirect(url_for('redirectUser', name = userName))

@app.route("/user/<name>/")
def redirectUser(name):
    if name == 'admin':
        return redirect(url_for('adminPage'))
    else:
        return redirect(url_for('userPage', userName = name))

@app.route("/register/")
def registerUser():
    return render_template('register.html')

@app.route("/post_user", methods = ['POST'])
def post_user():
##    _User = User('Username', 'Password')
    _User = Users(request.form["Username"], request.form["Password"])
    db.session.add(_User)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/admin_page/")
def adminPage():
    return render_template('hello.html', name = 'Admin')

@app.route("/user_page/<userName>/")
def userPage(userName):
    return render_template('hello.html', name = userName)


if __name__ == "__main__":
    app.run()
