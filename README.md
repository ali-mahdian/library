# library
Library Management System
This project manages a library via FastAPI. It's a simple project with FastAPI, PostgreSQL, Redis, Elasticsearch. 
There are two types of users: member & librarian; they can register, sign in and sign out.
A libraraian can add a book(No one else is allowed to do that) and members can reserve and return books. 
They have to return books within 14 days and there is a penalty for each day delay.
