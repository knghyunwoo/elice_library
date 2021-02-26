import csv
from datetime import date, datetime

from models import db, Book

session = db.session

with open('library.csv', 'r', encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for row in reader:
        published_at = datetime.strptime(
						row['publication_date'], '%Y-%m-%d').date()
        image_path = f"/static/image/{row['id']}"
        try:
            open(f'webproject/{image_path}.png')
            image_path += '.png'
        except:
            image_path += '.jpg'

        book = Book(
            id=int(row['id']), 
            name=row['book_name'], 
            publisher=row['publisher'],
            author=row['author'], 
            published_at=published_at, 
            page_count=int(row['pages']),
            isbn=row['isbn'], 
            description=row['description'], 
            image_path=image_path,
            stock=5,
            rating=0,
        )
        session.add(book)

    session.commit()