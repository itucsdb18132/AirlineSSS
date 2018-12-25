Parts Implemented by Muhammed Said Dikici
=========================================

Tickets Table
------------

Fields of Tickets Table
^^^^^^^^^^^^^^^^^^^^^^^
	
===========	=========	=======================	===========	================
FIELD NAME	TYPE		DETAILS			PRIMARY KEY	FOREIGN KEY REF.
===========	=========	=======================	===========	================
FLIGHT_ID	INTEGER		ID of flight		X		FLIGHTS
TICKET_ID	INTEGER		ID of ticket		X	
USERNAME	VARCHAR		Owner of the ticket			USERS
PRICE		NUMERIC		Price after discount		 			
CLASS		CHARACTER	Economy-Business class		 			
SEAT_NUMBER	INTEGER		Seat number of ticket			
RATE		NUMERIC		1 - Discount rate				
BASE_PRICE	NUMERIC		Price without discount	
==========	=========  	=======================	===========	================

Test Table
^^^^^^^^^^
=====  =====  =======
A      B      A and B
=====  =====  =======
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =======

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | - Table cells       |
+------------------------+ span rows. | - contain           |
| body row 4             |            | - body elements.    |
+------------------------+------------+---------------------+
	
TICKETS TABLE CREATE CODE
^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: /../../dbinit.py
   :language: python
   :linenos:
   :caption: Tickets Table
   :name: Tickets
   :lines: 126-146
