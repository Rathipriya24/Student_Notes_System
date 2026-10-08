# Student Notes Sharing System

A web-based Student Notes Sharing System developed using Flask, Python and MySQL.

## 📌 Project Overview

This project allows students to register, log in, upload study notes and view/download notes shared by other students.

An admin can manage uploaded notes through the admin dashboard.

## 🚀 Features

- Student Registration and Login
- Student Dashboard
- Upload Study Notes
- View and Download Notes
- Admin Login
- Admin Dashboard
- Approve or Reject Uploaded Notes
- MySQL Database Integration
- Secure configuration using Environment Variables

## 🛠️ Technologies Used

- Python
- Flask
- MySQL
- HTML
- CSS
- Jinja2
- python-dotenv

## 📂 Project Structure

```text
Student_Notes_System/
│
├── app.py
├── test_mysql.py
├── .gitignore
├── README.md
│
├── templates/
│   ├── admin.html
│   ├── admin_dashboard.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── upload.html
│   └── view_notes.html
│
└── static/
    └── style.css
