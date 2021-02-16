# Project 1

ENGO 551

After running application.py, you can get to the login page. If you already have an account, you can login to get to the next page. Otherwise, you need to click the sign in button to register first.

Once you log in, you will get to the home page, where you can view the books in the database. And you can search for books you like through searching for ISBN, author or title of the books. 

After clicking the book, you can get to a page with the details of the book. And you can also write your review about the book and give a rating from 1-5. The information of Google Book Review Data can also be found on this page. Each user can only write one review and rate once for each book. And you can also read your review on this page after submitting. 

After getting the ISBN of the book on book_info page, you can get to /api/<isbn> route to get the JSON respond of the book. 