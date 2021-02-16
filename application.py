import os, requests

from flask import Flask, session, request, render_template, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# # Check for environment variable
# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine("postgresql://postgres:@localhost/xielanting")
db = scoped_session(sessionmaker(bind=engine))


def googlebooks(isbn):
	res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:"+isbn})
	print(res.json())
	return res.json()


@app.route("/")
def index():

	if 'user_id' in session:
		user = db.execute('SELECT * FROM users WHERE id = :id', {'id':session['user_id']}).fetchone()
		if user:
			return render_template('home.html', user = user)
	else:
		return render_template('login.html')


@app.route('/register_user')
def register_user():
	return render_template('register.html')


@app.route('/register', methods = ["POST"])
def register():

	username = request.form.get('username')
	password = request.form.get('password')
	verify_password = request.form.get('verify_password')

	if password != verify_password:
		return render_template('message.html', primary_message = 'Error Occurs', message = 'Password do not match')
	elif db.execute('SELECT * FROM users WHERE username = :username', {'username':username}).rowcount != 0:
		return render_template('message.html', primary_message = 'Error Occurs', message = 'User ' + username + ' already exits')
	else:
		db.execute('INSERT INTO users (username, password) VALUES (:username, :password)',{'username':username, 'password':password})
		db.commit()
		return render_template('message.html', primary_message = 'Succesfully registered', message = 'Getting Strated!')


@app.route('/login', methods=["POST", 'GET'])
def login():

	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		user = db.execute('SELECT * FROM users WHERE username = :username',{'username':username}).fetchone()

		if user:
			if user.password == password:
				session['user_id'] = user.id
				return render_template('home.html', user = user)
			else:
				return render_template('message.html', primary_message = 'Error', message = 'Wrong password or username')
		else:
			return render_template('message.html', primary_message = 'Error', message = "Wrong password or username")
	else:
		if 'user_id' in session:
			user = db.execute('SELECT * FROM users WHERE id = :id', {'id':session['user_id']}).fetchone()
			if user:
				return render_template('home.html', user = user)
	return render_template('login.html')


@app.route('/logout')
def logout():

	session.clear()
	return render_template('login.html')


@app.route('/books', methods=['POST', 'GET'])
def books():

	if 'user_id' not in session:
		return render_template('login.html')

	search_type = None
	search = None
	books = db.execute('SELECT * FROM books').fetchall()
	if request.method == 'POST':
		search_type = request.form.get('search_type')
		search = request.form.get('search')

	if( search_type or search) is None:
		return render_template('books.html',books = books, status = True)

	if search_type.lower() == 'isbn':
		search_result = db.execute("SELECT * FROM books WHERE isbn LIKE :search", {'search':'%' + search + '%'}).fetchall()
	elif search_type.lower() == 'author':
		search_result = db.execute("SELECT * FROM books WHERE author LIKE :search", {'search':'%' + search + '%'}).fetchall()
	else:
		search_result = db.execute("SELECT * FROM books WHERE title LIKE :search", {'search':'%' + search + '%'}).fetchall()

	if search_result != None:
		if len(search_result)==0:
			search_result = None

	if search_result is not None:
		return render_template('books.html', books = search_result, status = True)

	else:
		return render_template('books.html', books = None, status = False)

	return render_template('books.html', books = books, status = True)


@app.route('/books/<int:book_id>', methods = ['POST', 'GET'])
def book_info(book_id):

	book_id = int(book_id)
	book_review = False
	user = None
	review = None
	review_conf = None
	rating_conf = None

	print(book_review)
	book = db.execute('SELECT * FROM books WHERE id = :id', {'id':book_id}).fetchone()
	if 'user_id' in session:

		user = db.execute('SELECT * FROM users WHERE id = :id',{'id':session['user_id']}).fetchone()
		review = db.execute('SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id',{'book_id':book_id, 'user_id':session['user_id']}).fetchone()

		if review:
			book_review = True
			review_conf = review.review
			rating_conf = review.rating
			
		else:
			if request.method == 'POST':
				review_conf = request.form.get('Review')
				rating_conf = int(request.form.get('rating'))
				if review_conf and rating_conf:
					db.execute('INSERT INTO reviews (review, user_id, book_id, rating) VALUES (:review, :user_id, :book_id, :rating)',
						{'review':review_conf, 'user_id':user.id, 'book_id':book_id, 'rating':rating_conf})
					db.commit()
					book_review = True
				else:
					return render_template('message.html', primary_message= 'Error', 
						message= 'You did not fill any rating or reivew!')

	googlebook = googlebooks(isbn = book.isbn)
	googlebook=googlebook["items"][0]["volumeInfo"]
	return render_template('book_info.html', book = book, book_review = book_review, 
		review = review_conf,rating = rating_conf, google_review = googlebook, user = user)

@app.route('/api/<string:isbn>')
def book_api(isbn):
	book = db.execute('SELECT * FROM books WHERE isbn = :isbn', {'isbn':isbn}).fetchone()
	googlebook = googlebooks(isbn = book.isbn)
	googlebook=googlebook["items"][0]["volumeInfo"]
	if book is None:
		return jsonify({'error':'invalid ISBN'}),404               
	return jsonify({
        'title':book.title,
        'author':book.author,
        'year':book.year,
        'isbn':isbn,
        'review_count':googlebook['ratingsCount'],
        'average_rating':googlebook['averageRating']
        })

if __name__=="__main__":
	app.run()