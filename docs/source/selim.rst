Tables Implemented by Selim Enes Kılıçaslan
===========================================

*Person Table*
--------------

A - Fields of Person Table
^^^^^^^^^^^^^^^^^^^^^^^^^^
	
	============	=========	====================	===========	================
	FIELD NAME	TYPE		DETAILS			PRIMARY KEY	FOREIGN KEY REF.
	============	=========	====================	===========	================
	USERNAME	VARCHAR		Username		X		USERS
	FULLNAME	VARCHAR		User's fullname			
	EMAILADDRESS	VARCHAR		User's email address			
	USERROLE	CHARACTER	Admin or User		 			
	BALANCE		NUMERIC		Balance		 			
	============	=========  	====================	===========	================

	
B - Person Table Create Statement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	.. literalinclude:: /../../dbinit.py
	   :language: sql
	   :linenos:
	   :caption: Person Table
	   :name: Person
	   :lines: 17-28

*Payments Table*
----------------

A - Fields of Payments Table
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	
	===========	=========	===================	===========	================
	FIELD NAME	TYPE		DETAILS				PRIMARY KEY	FOREIGN KEY REF.
	===========	=========	===================	===========	================
	PAYMENTID	SERIAL		Payment ID			X			
	USERNAME	VARCHAR		Username						USERS
	AMOUNT		NUMERIC		Requested amount			
	APPROVED	CHARACTER	Request status		 			
	APPROVED_BY	NUMERIC		Request approved by		 			
	===========	=========  	===================	===========	================

	
B - Payments Table Create Statement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	.. literalinclude:: /../../dbinit.py
	   :language: sql
	   :linenos:
	   :caption: Payments Table
	   :name: Payments
	   :lines: 31-45
