Tables Implemented by Selim Enes Kılıçaslan
===========================================

*Person Table*
--------------

A - Fields of Person Table
^^^^^^^^^^^^^^^^^^^^^^^^^^
	
	============	=========	====================	===========	================
	FIELD NAME	TYPE		DETAILS			PRIMARY KEY	FOREIGN KEY REF.
	============	=========	====================	===========	================
	USERNAME	VARCHAR		Username		X		USERS-USERNAME
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
	FIELD NAME	TYPE		DETAILS			PRIMARY KEY	FOREIGN KEY REF.
	===========	=========	===================	===========	================
	PAYMENTID	SERIAL		Payment ID		X			
	USERNAME	VARCHAR		Username				USERS-USERNAME
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
	   
*Posts Table*
-------------

A - Fields of Posts Table
^^^^^^^^^^^^^^^^^^^^^^^^^
	
	===========	========	==================	===========	================
	FIELD NAME	TYPE		DETAILS			PRIMARY KEY	FOREIGN KEY REF.
	===========	========	==================	===========	================
	POSTID		SERIAL		Post ID			X			
	POSTER		VARCHAR		Username of poster			USERS-USERNAME
	CONTENT		VARCHAR		Post content			
	DATE		NUMERIC		Posting date			
	TIME		NUMERIC		Posting time			
	TITLE		VARCHAR		Post title		 			
	IMAGE		INTEGER		Image ID		 		UPLOADS-ID
	===========	========  	==================	===========	================

	
B - Posts Table Create Statement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	.. literalinclude:: /../../dbinit.py
	   :language: sql
	   :linenos:
	   :caption: Posts Table
	   :name: Posts
	   :lines: 55-71

*Uploads Table*
---------------

A - Fields of Posts Table
^^^^^^^^^^^^^^^^^^^^^^^^^
	
	===========	========	==================	===========	================
	FIELD NAME	TYPE		DETAILS				PRIMARY KEY	FOREIGN KEY REF.
	===========	========	==================	===========	================
	ID			SERIAL		Post ID				X			
	FILENAME	VARCHAR		Filename			
	DATA		BYTEA		Binary data			
	===========	========  	==================	===========	================

	
B - Posts Table Create Statement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	.. literalinclude:: /../../dbinit.py
	   :language: sql
	   :linenos:
	   :caption: Posts Table
	   :name: Posts
	   :lines: 48-52
