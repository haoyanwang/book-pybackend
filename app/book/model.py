from .. import myDb

db = myDb['book-test-1']


class Book():
    def __init__(self):
        pass

    def get_bookId_by_bookName(bookName):
        return db.find_one({"book_name": bookName}, {"_id": 0, "book_id": 1})['book_id']

    def get_bookName_by_bookId(bookId):
        return db.find_one({"book_id":bookId},{"_id":0,"book_name":1})['book_name']

    def get_book_by_bookId(bookId):
        return db.find_one({"book_id":bookId},{"_id":0})
