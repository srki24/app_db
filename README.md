# app_db

Tested on Windows, Kivy might not work on different OS.


Postgres database app made in python with kivy, and psycopg2 . 

The app was made for a school project, with a prerequisition that querry errors are shown to the final user.

A real business procedure was ised to ilustrate different database and application requirements.

The database itself was normalized at first, and then optimized later with a few denormalisation instances.
It also contains different indices, triggers and user defined types which were made in accordance with project requests.
Database is deployed on an ElephantSQL server.


Files organization:

Design.kv file contains all of the front-end related stuff (mostly regarding different widgets and screens) 

Python logic of the widgets is organized in the following way:

  - main.py file has app builder in it. It is used for starting the app.

  - files Main Screen, Correspondence, Users, Requests and Status present different screens in the app itself.
 Each one, with different classes and functions, is saved as a different file, named accordingly.
  
  - backend.py file contains all of SQL querries used for the communication with the database.


.env file is used for opening connection with the database.

App_db file contains a backup of the database itself.

requirements.txt contains all of the different python modules used in this project.
