import mysql.connector

connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rathi2402",
    database="student_notes_db"
)

if connection.is_connected():
    print("MySQL connected successfully!")

connection.close()
