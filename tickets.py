import psycopg2 as dbapi2
from flask import redirect, url_for, request, session, flash
from general import RenderTemplate, refreshUserData, ifAdmin
import decimal

dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""

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

            statement = """SELECT bsn_capacity, eco_capacity FROM flights
            INNER JOIN planes ON planes.plane_id = flights.plane_id
            WHERE flight_id ='%s'
            """
            cursor.execute(statement, (flight_id))
            capacities = cursor.fetchone()
            bsn_capacity = capacities[0]
            eco_capacity = capacities[1]

            for i in range(bsn_capacity):
                statement = """INSERT INTO tickets(flight_id, ticket_id, price, class, base_price) VALUES(%s, %s, %s, 'B', %s)
                """

                cursor.execute(statement, (flight_id, bsnticketid, bsnprice, bsnprice))
                bsnticketid += 1
                bsnprice += 10
            ecoticketid = bsn_capacity + 1
            for i in range(eco_capacity):
                statement = """INSERT INTO tickets(flight_id, ticket_id, price, class, base_price) VALUES(%s, %s, %s, 'E', %s)
                """

                cursor.execute(statement, (flight_id, ecoticketid, eco_first_ticket_price, eco_first_ticket_price))
                ecoticketid += 1
                eco_first_ticket_price += 5
            connection.commit()
        except dbapi2.DatabaseError:
            connection.rollback()
            return redirect(url_for('errorpage', message="Error in Create Tickets Function!"))
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message='Please log in first'))

def view_tickets():
    if 'Username' in session:
        refreshUserData()
        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            username = session['Username']
            statement = """SELECT f.flight_id, ticket_id, seat_number, class, a.airport_name, air.airport_name, departure_time, arrival_time  FROM tickets AS t
                        INNER JOIN flights AS f ON f.flight_id = t.flight_id
                        INNER JOIN airports AS a ON a.airport_id = f.departure_id
                        INNER JOIN airports AS air ON air.airport_id = f.destination_id
                        WHERE t.username = '%s'
                        """ % username
            cursor.execute(statement)
            ticket_info = cursor.fetchall()
            return RenderTemplate('view_tickets.html', tickets= ticket_info)
        except dbapi2.DatabaseError:
            connection.rollback()
            return redirect(url_for('errorpage', message="Error in View Tickets Function !"))
        finally:
            connection.close()
    else:
        return redirect(url_for('errorpage', message='Please log in first'))

@app.route('/check_in', methods=['GET', 'POST'])
def check_in():
    if 'Username' in session:
        refreshUserData()
        if request.method == 'GET':
            try:
                flight_id = request.args['fId']
                ticket_id = request.args['tId']
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """
                    SELECT ticket_id FROM tickets
                        WHERE flight_id = %s
                          AND ticket_id = %s
                          AND username  = %s
                """
                cursor.execute(statement, (flight_id, ticket_id, session['Username']))
                if cursor.rowcount != 1:
                    return redirect(url_for('errorpage', message="Ticket not found!"))
                statement = """
                    SELECT ticket_id FROM tickets
                        WHERE flight_id = %s
                          AND seat_number IS NULL
                          AND class = (SELECT class FROM tickets
                                        WHERE flight_id = %s
                                          AND ticket_id = %s)
                    ORDER BY ticket_id ASC
                """
                cursor.execute(statement, (flight_id, flight_id, ticket_id))
                emptyseats = cursor.fetchall()
                return RenderTemplate('check_in.html', fullname=session['Fullname'], emptyseats=emptyseats, flightID=flight_id, ticketID=ticket_id)

            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata!"
            finally:
                connection.close()
        else:
            try:
                flight_id = request.args['fId']
                ticket_id = request.args['tId']
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """
                    SELECT ticket_id FROM tickets
                        WHERE flight_id = %s
                          AND ticket_id = %s
                          AND username  = %s
                """
                cursor.execute(statement, (flight_id, ticket_id, session['Username']))
                if cursor.rowcount != 1:
                    return redirect(url_for('errorpage', message = "Ticket not found!"))

                seat_number = request.form['seat']
                statement = """
                    SELECT ticket_id FROM tickets
                        WHERE flight_id = %s
                          AND ticket_id = %s
                          AND seat_number  = %s
                """
                cursor.execute(statement, (flight_id, ticket_id, seat_number))
                if cursor.rowcount > 0:
                    flash("Seat already taken!")
                    return redirect(url_for('view_tickets'))
                statement = """
                    UPDATE tickets SET seat_number = %s
                        WHERE flight_id = %s
                          AND ticket_id = %s
                """
                cursor.execute(statement, (seat_number, flight_id, ticket_id))
                connection.commit()
                flash("You have successfully checked-in")
                return redirect(url_for('view_tickets'))

            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata!"
            finally:
                connection.close()
    else:
        return redirect(url_for('errorpage', message = 'Please log in first'))