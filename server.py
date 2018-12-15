from flask import Flask
import admin
import flights
import general
import tickets
import user
import datetime
import psycopg2 as dbapi2
from base64 import b64encode

app = Flask(__name__)
app.debug = True

dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""



#Sercan
@app.route('/')
def index():
    general.refreshUserData()
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

        statement = """SELECT DISTINCT t.rate, t.flight_id, c.city, c2.city FROM tickets AS t
                        INNER JOIN flights AS f ON f.flight_id = t.flight_id
                        INNER JOIN airports AS a1 ON a1.airport_id = f.departure_id
                        INNER JOIN airports AS a2 ON a2.airport_id = f.destination_id
                        INNER JOIN cities AS c ON c.city_id = a1.city_id
                        INNER JOIN cities AS c2 ON c2.city_id = a2.city_id
                        WHERE t.rate < 1
                        ORDER BY t.rate ASC
                        LIMIT 10
                    """
        cursor.execute(statement)
        discount = cursor.fetchall()
        images = {}
        for post in posts:
            images[post[0]] = b64encode(post[5]).decode('utf-8')
        return general.RenderTemplate('index.html', cities=cities, date=date, discount=discount, homeActive='active', posts=posts, images=images)
    except dbapi2.DatabaseError as e:
        connection.rollback()
        return str(e)
    finally:
        connection.close()





def create_app():
    app = Flask(__name__)

    #General Definitions
    app.add_url_rule("/", view_func=index) #Sercan
    app.add_url_rule("/errorpage/<message>", view_func=general.errorpage) #Enes
    app.add_url_rule("/about", view_func=general.about) #Enes
    app.add_url_rule("/news", view_func=general.news) #Enes

    #Admin Definitions
    app.add_url_rule("/adm_sendpost", view_func=admin.adm_sendpost, methods = ['GET', 'POST']) #Enes
    app.add_url_rule("/adm_pymreqs", view_func=admin.adm_pymreqs, methods = ['GET', 'POST']) #Enes
    app.add_url_rule("/adm_updateflight", view_func=admin.adm_updateflight, methods = ['GET', 'POST'])
    app.add_url_rule("/adm_deleteflight", view_func=admin.adm_deleteflight, methods=['GET', 'POST'])
    app.add_url_rule("/deleteuser/<username>", view_func=admin.deleteuser, methods = ['POST']) #Enes
    app.add_url_rule("/adm_updateuser/<username>", view_func=admin.adm_updateuser, methods = ['POST']) #Enes
    app.add_url_rule("/adm_users/<username>", view_func=admin.updateuser) #Enes
    app.add_url_rule("/adminpage", view_func=admin.adminpage) #Enes
    app.add_url_rule("/adm_users", view_func=admin.adm_users) #Enes
    app.add_url_rule("/adm_fabrika_ayarlari", view_func=admin.adm_fabrika_ayarlari) #Enes

    #Flights Definitions
    app.add_url_rule("/flights", view_func=flights.flights) #Sercan
    app.add_url_rule("/searchList", view_func=flights.searchList, methods = ['GET', 'POST']) #Sercan
    app.add_url_rule("/roundFlight", view_func=flights.roundFlight, methods = ['GET', 'POST']) #Sercan
    app.add_url_rule("/addPlane", view_func=flights.addPlane, methods = ['GET', 'POST']) #Sercan
    app.add_url_rule("/discount", view_func=flights.discount, methods = ['GET', 'POST']) #Sercan

    #Tickets Definitions
    app.add_url_rule("/tickets", view_func=tickets.view_tickets) #Said
    app.add_url_rule("/buy_ticket/<int:flight_id>", view_func=tickets.buy_ticket, methods = ['GET', 'POST']) #Said
    app.add_url_rule("/check_in", view_func=tickets.check_in, methods = ['GET', 'POST']) #Said

    #User Definitons
    app.add_url_rule("/login", view_func=user.login, methods = ['POST']) #Enes
    app.add_url_rule("/register", view_func=user.register, methods = ['POST']) #Enes
    app.add_url_rule("/userpage", view_func=user.userpage) #Enes
    app.add_url_rule("/logout", view_func=user.logout) #Enes
    app.add_url_rule("/buycoins", view_func=user.buycoins, methods = ['GET', 'POST']) #Enes
    app.add_url_rule("/edituser", view_func=user.edituser, methods = ['GET', 'POST']) #Enes
    app.add_url_rule("/forgotpassword", view_func=user.forgotpassword, methods = ['GET', 'POST']) #Enes

    return app


if __name__ == "__main__":
    app = create_app()
    app.config.update(dict(
    SECRET_KEY="pnBM(@?&#p]l~eI%L&$@#9f)T^uK7U",
    WTF_CSRF_SECRET_KEY="N4<*$83/[[{)ZO&X2yL_qN68+{;;Xo"
    ))
    app.run()
