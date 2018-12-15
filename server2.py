from flask import Flask
import admin
import flights
import general
import tickets
import user

app = Flask(__name__)
app.debug = True



dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""


def create_app():
    app = Flask(__name__)

    #General Definitions
    app.add_url_rule("/", view_func=general.index)
    app.add_url_rule("/errorpage/<message>", view_func=general.errorpage)
    app.add_url_rule("/about", view_func=general.about)
    app.add_url_rule("/news", view_func=general.news)

    #Admin Definitions
    app.add_url_rule("/adm_sendpost", view_func=admin.adm_sendpost, methods = ['GET', 'POST'])
    app.add_url_rule("/adm_pymreqs", view_func=admin.adm_pymreqs, methods = ['GET', 'POST'])
    app.add_url_rule("/adm_updateflight", view_func=admin.adm_updateflight, methods = ['GET', 'POST'])
    app.add_url_rule("/deleteuser/<username>", view_func=admin.deleteuser, methods = ['POST'])
    app.add_url_rule("/adm_updateuser/<username>", view_func=admin.adm_updateuser, methods = ['POST'])
    app.add_url_rule("/adm_users/<username>", view_func=admin.updateuser)
    app.add_url_rule("/adminpage", view_func=admin.adminpage)
    app.add_url_rule("/adm_users", view_func=admin.adm_users)

    #Flights Definitions
    app.add_url_rule("/flights", view_func=flights.flights)
    app.add_url_rule("/searchList", view_func=flights.searchList, methods = ['GET', 'POST'])
    app.add_url_rule("/roundFlight", view_func=flights.roundFlight, methods = ['GET', 'POST'])
    app.add_url_rule("/addPlane", view_func=flights.addPlane, methods = ['GET', 'POST'])
    app.add_url_rule("/discount", view_func=flights.discount, methods = ['GET', 'POST'])

    #Tickets Definitions
    app.add_url_rule("/tickets", view_func=tickets.view_tickets)
    app.add_url_rule("/buy_ticket/<int:flight_id>", view_func=tickets.buy_ticket, methods = ['GET', 'POST'])
    app.add_url_rule("/check_in", view_func=tickets.check_in, methods = ['GET', 'POST'])

    #User Definitons
    app.add_url_rule("/login", view_func=user.login, methods = ['POST'])
    app.add_url_rule("/register", view_func=user.register, methods = ['POST'])
    app.add_url_rule("/userpage", view_func=user.userpage)
    app.add_url_rule("/logout", view_func=user.logout)
    app.add_url_rule("/buycoins", view_func=user.buycoins, methods = ['GET', 'POST'])
    app.add_url_rule("/edituser", view_func=user.edituser, methods = ['GET', 'POST'])
    app.add_url_rule("/forgotpassword", view_func=user.forgotpassword, methods = ['GET', 'POST'])

    return app


if __name__ == "__main__":
    app = create_app()
    app.config.update(dict(
    SECRET_KEY="pnBM(@?&#p]l~eI%L&$@#9f)T^uK7U",
    WTF_CSRF_SECRET_KEY="N4<*$83/[[{)ZO&X2yL_qN68+{;;Xo"
    ))
    app.run()
