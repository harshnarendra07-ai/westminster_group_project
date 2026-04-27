Sky Engineering Health Check System
-----------------------------------
Module: 5COSC021W Software Development Group Project

How to set up and run the project:

Step 1: Extract the ZIP file to a local directory on your computer.

Step 2: Open your terminal or command prompt. 

Step 3: Navigate into the extracted project folder (you must be in the same folder that contains the 'manage.py' file).

Step 4: Install the required Python packages by running the following command:
pip install django xhtml2pdf Pillow

Step 5: Start the local development server by running the following command:
python manage.py runserver

Step 6: Open a web browser and go to the following URL to access the application:
http://127.0.0.1:8000/

-----------------------------------
Important Note regarding the Database:

The database (db.sqlite3) is already included and fully populated with all Departments, Teams, Dependencies, and Engineers required by the coursework brief. You do not need to run any import scripts or make migrations.

-----------------------------------

Login Credentials:

Admin Account (For accessing the Django Admin Dashboard, User Management, and Audit Logs):
Username: admin
Password: skyproject123

Standard Engineer Account (For testing standard routing, team views, and schedules):
Username: agile_squad_eng_1
Password: skyengineering123