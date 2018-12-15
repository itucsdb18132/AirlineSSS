from flask import redirect, url_for, request, flash
import psycopg2 as dbapi2
from general import RenderTemplate, refreshUserData, ifAdmin

dsn = """user='kbktqbcfmdxpbw' password='76006678dc4edef0501db56d75112cacde489dfb1be1648833f8ea853a1e32f4'
         host='ec2-54-247-101-191.eu-west-1.compute.amazonaws.com' port=5432 dbname='d1lo8nienmd3cn'"""

#Sercan
def searchList():
    departure = request.form['from']
    destination = request.form['to']
    departure_time = request.form['date']
    try:
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """SELECT f.flight_id,a.airport_name, c.city, a2.airport_name, c2.city, f.departure_time, f.arrival_time FROM flights AS f
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

#Sercan
def flights():

        try:
            connection = dbapi2.connect(dsn)
            cursor = connection.cursor()
            statement = """SELECT f.flight_id,a.airport_name, c.city, a2.airport_name, c2.city, f.departure_time, f.arrival_time FROM flights AS f
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

#Sercan
def roundFlight():
    departure = request.form['from']
    destination = request.form['to']
    departure_time = request.form['date']
    departure_time2 = request.form['date2']
    destination2 = request.form['from']
    departure2 = request.form['to']
    try:
        connection = dbapi2.connect(dsn)
        cursor = connection.cursor()
        statement = """SELECT f.flight_id,a.airport_name, c.city, a2.airport_name, c2.city, f.departure_time, f.arrival_time FROM flights AS f
                                            INNER JOIN airports AS a ON f.departure_id = a.airport_id
                                            INNER JOIN airports AS a2 ON f.destination_id = a2.airport_id
                                            INNER JOIN planes AS p ON f.plane_id = p.plane_id
                                            INNER JOIN cities AS c ON a.city_id = c.city_id
                                            INNER JOIN cities AS c2 ON a2.city_id = c2.city_id
                                            WHERE c.city = %s AND c2.city = %s AND f.departure_time::text LIKE %s"""
        departure_time += '%'
        cursor.execute(statement, (departure, destination, departure_time))
        rows = cursor.fetchall()
        statement = """SELECT f.flight_id,a.airport_name, c.city, a2.airport_name, c2.city, f.departure_time, f.arrival_time FROM flights AS f
                                                    INNER JOIN airports AS a ON f.departure_id = a.airport_id
                                                    INNER JOIN airports AS a2 ON f.destination_id = a2.airport_id
                                                    INNER JOIN planes AS p ON f.plane_id = p.plane_id
                                                    INNER JOIN cities AS c ON a.city_id = c.city_id
                                                    INNER JOIN cities AS c2 ON a2.city_id = c2.city_id
                                                    WHERE c.city = %s AND c2.city = %s AND f.departure_time::text LIKE %s"""
        departure_time2 += '%'
        cursor.execute(statement, (departure2, destination2, departure_time2))
        rows2 = cursor.fetchall()
        return RenderTemplate('roundFlight.html', flights=rows, flightss=rows2, flightsActive='active')
    except dbapi2.DatabaseError as e:
        connection.rollback()
        return str(e)
    finally:
        connection.close()

#Sercan
def addPlane():
    refreshUserData()
    if ifAdmin():
        if request.method == 'POST':
            planeid = request.form['planeId']
            planemodel = request.form['planeModel']
            bsncap = request.form['bsnCap']
            ecocap = request.form['ecoCap']
            try:
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """ INSERT INTO planes (plane_id, plane_model, bsn_capacity, eco_capacity)
                                                VALUES (%s, %s,%s,%s)
                                        """
                cursor.execute(statement, (planeid, planemodel, bsncap, ecocap))
                connection.commit()

                return RenderTemplate('addPlane.html', adminActive='active')
            except dbapi2.DatabaseError:
                connection.rollback()
                return "Hata2!"
            finally:
                connection.close()
        else:
            return RenderTemplate('addPlane.html')

    else:
        return redirect(url_for('errorpage', message='Not Authorized!'))

#Sercan
def discount():
    if ifAdmin():
        refreshUserData()
        if request.method == 'GET':
            try:
                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """SELECT f.flight_id,a.airport_name, c.city, a2.airport_name, c2.city, f.departure_time, f.arrival_time FROM flights AS f

                                            INNER JOIN airports AS a ON f.departure_id = a.airport_id
                                            INNER JOIN airports AS a2 ON f.destination_id = a2.airport_id
                                            INNER JOIN planes AS p ON f.plane_id = p.plane_id
                                            INNER JOIN cities AS c ON a.city_id = c.city_id
                                            INNER JOIN cities AS c2 ON a2.city_id = c2.city_id
                                        """
                cursor.execute(statement)
                rows = cursor.fetchall()

                return RenderTemplate('discount.html', flights=rows, flightsActive='active')
            except dbapi2.DatabaseError as e:
                connection.rollback()
                return str(e)
            finally:
                connection.close()
        else :
            try:
                _id = request.form['id']
                _discount = request.form['discount_rate']
                rate = 1 - float(_discount)/100

                connection = dbapi2.connect(dsn)
                cursor = connection.cursor()
                statement = """ UPDATE tickets SET rate = %s
                                    WHERE flight_id = %s
                                    """
                cursor.execute(statement, (rate, _id))
                connection.commit()



                statement = """ UPDATE tickets SET price = base_price*rate
                                        WHERE flight_id = %s
                """ % _id
                cursor.execute(statement)
                connection.commit()
                flash('Discount has been set')
                return RenderTemplate('discount.html', adminActive='active')
            except dbapi2.DatabaseError as e:
                connection.rollback()
                return str(e)
            finally:
                connection.close()
    else:
        return redirect(url_for('errorpage', message = 'Not Authorized!'))