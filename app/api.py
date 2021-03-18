from fastapi import FastAPI, Body, Depends, HTTPException
from passlib.context import CryptContext
from datetime import date, timedelta
import elasticsearch

from app.model import UserSchema, UserLoginSchema, BookSchema, BookOperationSchema
from main import con, cur, es
from app.auth.auth_handler import signJWT
from app.auth.auth_bearer import JWTBearer, LibrarianBearer, MemberBearer

due_time = timedelta(days=+14)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


@app.post("/signup", tags=["users"])
async def create_user(user: UserSchema = Body(...)):
    cur.execute(f"SELECT email FROM users WHERE email='{user.email}';")
    if cur.fetchall():  # if there is already a user with that email
        return HTTPException(status_code=409, detail="Email already taken, Try new one!")
    else:
        hashed_password = pwd_context.hash(user.password)
        cur.execute(f'''INSERT INTO users (email, password, role) 
            VALUES('{user.email}','{hashed_password}','{user.role}');''')
    con.commit()
    return {"message": f"{user.email} as a {user.role} created successfully!"}


@app.post("/login", tags=["users"])
async def login_user(user: UserLoginSchema = Body(...)):
    cur.execute(f"SELECT * FROM users WHERE email='{user.email}';")
    data = cur.fetchall()
    if data:
        hashed = data[0][2]  # hashed password from database
        if pwd_context.verify(user.password, hashed):
            user_id = data[0][0]
            user_role = data[0][3]
            return {"token": signJWT(user_id, user_role)}
        else:
            return {"error": f"Wrong password for {user.email}!"}
    else:
        return {"error": "Wrong email!"}


@app.get("/logout",  dependencies=[Depends(JWTBearer())], tags=["users"])
async def logout_user():
    return {"message": "logged out!"}


@app.post("/book/add", dependencies=[Depends(LibrarianBearer())], tags=["books"])
async def add_book(book: BookSchema):
    cur.execute(f"SELECT title FROM book WHERE title='{book.title}';")
    if cur.fetchall():  # if there is already a book with that title
        return {"error": "Book already exists at the library!"}
    else:
        cur.execute(f'''INSERT INTO book (title, author, des) 
            VALUES('{book.title}','{book.author}', '{book.des}');''')
        con.commit()
        body = {"title": f'"{book.title}"'}
        es.index(index='library', doc_type='book', body=body)
    return {"message": f"{book.title} by {book.author} added successfully!"}


@app.post("/book/reserve", tags=["books"])
async def reserve_book(book: BookOperationSchema, current_user_id=Depends(MemberBearer())):
    cur.execute(f"SELECT borrowed_by FROM book WHERE title='{book.title}';")
    data = cur.fetchall()
    if data:  # if there exists a book with that title
        if data[0][0] is None:  # check if available
            cur.execute(f'''UPDATE book SET borrowed_by = {current_user_id}, date_borrowed = NOW()::DATE
                WHERE title = '{book.title}';''')
            con.commit()
            cur.execute(f"SELECT date_borrowed FROM book WHERE title='{book.title}';")
            date_borrowed = cur.fetchall()[0][0]
            deadline = date_borrowed + due_time
            return {"message": f"you borrowed {book.title} successfully!please return in until {deadline}"}
        else:  # if the book is borrowed before
            return {"error": "Book is not available right now, Try later!"}
    else:
        return {"error": "Book not found!"}


@app.post("/book/return", tags=["books"])
async def return_book(book: BookOperationSchema, current_user_id=Depends(MemberBearer())):
    cur.execute(f"SELECT borrowed_by FROM book WHERE title='{book.title}';")
    data = cur.fetchall()
    if data:  # if there exists a book with that title
        if data[0][0] != current_user_id:
            return {"error": "you have not borrowed this book!"}
        else:  # take back book
            cur.execute(f"SELECT date_borrowed FROM book WHERE title='{book.title}';")
            date_borrowed = cur.fetchall()[0][0]
            latency = date.today() - (date_borrowed + due_time)
            print(latency)
            cur.execute(f"UPDATE book SET borrowed_by = NULL, date_borrowed = NULL WHERE title = '{book.title}';")
            con.commit()
            if latency.days <= 0:
                return {"message": f"Thanks!you returned {book.title} in time."}
            else:
                penalty = latency.days * 100
                return {"message": f"Oops!you returned {book.title} late.Your penalty is {penalty}$"}
    else:
        return {"error": "Book not found!"}


@app.post("/book/search", tags=["books"])
async def search_book(keyword: str):
    try:
        result = es.search(index="library", body={"query": {"match": {"title": f'"{keyword}"'}}})
        return result['hits']['hits']
    except elasticsearch.exceptions.NotFoundError:
        return {"error": "No matching book found!"}


