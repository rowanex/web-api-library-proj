from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Base
from database import engine, SessionLocal
from typing import Set

from crud import (
    create_author, read_authors, read_author, update_author, delete_author,
    create_book, read_books, read_book, update_book_info, patch_book_info, delete_book
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

connected_clients: Set[WebSocket] = set()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect as e:
        print(f"WebSocket disconnected: {e}")
    finally:
        connected_clients.remove(websocket)
        print("WebSocket connection closed")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    authors = read_authors(db, skip=0, limit=10)
    books = read_books(db, skip=0, limit=10)
    return templates.TemplateResponse("index.html", {"request": request, "authors": authors, "books": books})


async def notify_clients(message: str):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except WebSocketDisconnect:
            pass


# authors
@app.get("/authors/")
async def read_authors_api(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        return read_authors(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/authors/{author_id}")
async def read_author_api(author_id: int, db: Session = Depends(get_db)):
    try:
        return read_author(db, author_id=author_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/authors/")
async def create_author_api(name: str, db: Session = Depends(get_db)):
    try:
        await notify_clients("Author created: {}".format(name))
        return create_author(db, name=name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/authors/{author_id}")
async def update_author_api(author_id: int, name: str, db: Session = Depends(get_db)):
    try:
        await notify_clients("Author putted: {}".format(name))
        return update_author(db, author_id=author_id, name=name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/authors/{author_id}")
async def delete_author_api(author_id: int, db: Session = Depends(get_db)):
    try:
        deleted_author = delete_author(db, author_id=author_id)
        if deleted_author:
            await notify_clients("Author deleted by id: {}".format(author_id))
            return {"status": "success", "message": "Author deleted successfully"}
        raise HTTPException(status_code=404, detail=f"Author with id {author_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# books
@app.get("/books/")
async def read_books_api(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        return read_books(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/books/{book_id}")
async def read_book_api(book_id: int, db: Session = Depends(get_db)):
    try:
        return read_book(db, book_id=book_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/books/{book_id}")
async def patch_book_info_api(book_id: int, title: str = None, genre: str = None, publish_date: str = None,
                              author_id: int = None, db: Session = Depends(get_db)):
    try:
        await notify_clients("Book patched: {}".format(book_id))
        return patch_book_info(db, book_id=book_id, title=title, genre=genre,
                               publish_date=publish_date, author_id=author_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/books/{book_id}")
async def update_book_info_api(book_id: int, title: str, genre: str, publish_date: str,
                               author_id: int, db: Session = Depends(get_db)):
    try:
        await notify_clients("Book putted: {}".format(book_id))
        return update_book_info(db, book_id=book_id, title=title, genre=genre,
                                publish_date=publish_date, author_id=author_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/books/")
async def create_book_api(title: str, genre: str, publish_date: str, author_id: int, db: Session = Depends(get_db)):
    try:
        await notify_clients("Books created: {}".format(title))
        return create_book(db, title=title, genre=genre, publish_date=publish_date, author_id=author_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/books/{book_id}")
async def delete_book_api(book_id: int, db: Session = Depends(get_db)):
    try:
        deleted_book = delete_book(db, book_id=book_id)
        if deleted_book:
            await notify_clients("Book deleted by id: {}".format(book_id))
            return {"status": "success", "message": "Book deleted successfully"}
        raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
