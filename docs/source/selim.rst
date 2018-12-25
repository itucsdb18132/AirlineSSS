Tables Implemented by Selim Enes Kılıçaslan
===========================================

*Person Table*
--------------

*  Fields of Person Table
^^^^^^^^^^^^^^^^^^^^^^^^^
	
	============	=========	====================	===========	================
	FIELD NAME	TYPE		DETAILS			PRIMARY KEY	FOREIGN KEY REF.
	============	=========	====================	===========	================
	USERNAME	VARCHAR		Username		X		USERS
	FULLNAME	VARCHAR		User's fullname			
	EMAILADDRESS	VARCHAR		User's email address			
	USERROLE	CHARACTER	Admin or User		 			
	BALANCE		NUMERIC		Balance		 			
	============	=========  	====================	===========	================

	
*  Person Table Create Statement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
	.. literalinclude:: /../../dbinit.py
	   :language: sql
	   :linenos:
	   :caption: Person Table
	   :name: Person
	   :lines: 17-28
