from sqlalchemy.orm import Session
import models
from datetime import datetime


def create_author(db: Session, name: str):
    db_author = models.Author(name=name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def read_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Author).offset(skip).limit(limit).all()


def read_author(db: Session, author_id: int):
    return db.query(models.Author).filter(models.Author.id == author_id).first()


def update_author(db: Session, author_id: int, name: str):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if db_author:
        db_author.name = name
        db.commit()
        db.refresh(db_author)
        return db_author
    return None


def delete_author(db: Session, author_id: int):
    db_author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if db_author:
        db.delete(db_author)
        db.commit()
        return db_author
    return None


def create_book(db: Session, title: str, genre: str, publish_date: str, author_id: int):
    publish_date = datetime.strptime(publish_date, '%d.%m.%y').date()
    db_book = models.Book(
        title=title,
        genre=genre,
        publish_date=publish_date,
        author_id=author_id
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def read_books(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Book).offset(skip).limit(limit).all()


def read_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.id == book_id).first()


def patch_book_info(db: Session, book_id: int, title: str, genre: str, publish_date: str, author_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        if title:
            db_book.title = title
        if genre:
            db_book.genre = genre
        if publish_date:
            db_book.publish_date = datetime.strptime(publish_date, '%d.%m.%y').date()
        if author_id:
            db_book.author_id = author_id
        db.commit()
        db.refresh(db_book)
        return db_book
    return None


def update_book_info(db: Session, book_id: int, title: str, genre: str, publish_date: str, author_id: int):
    publish_date = datetime.strptime(publish_date, '%d.%m.%y').date()
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        db_book.title = title
        db_book.genre = genre
        db_book.publish_date = publish_date
        db_book.author_id = author_id
        db.commit()
        db.refresh(db_book)
        return db_book
    return None


def delete_book(db: Session, book_id: int):
    db_book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if db_book:
        db.delete(db_book)
        db.commit()
        return db_book
    return None
