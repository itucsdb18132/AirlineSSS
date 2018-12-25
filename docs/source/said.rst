Parts Implemented by Muhammed Said Dikici
=========================================

Tickets Table
--------------

Fields of Tickets Table
^^^^^^^^^^^^^^^^^^^^^^^^
	
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
===========	=========  	=======================	===========	================

	
TICKETS TABLE CREATE CODE
^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: /../../dbinit.py
   :language: python
   :linenos:
   :caption: Tickets Table
   :name: Tickets
   :lines: 126-146
