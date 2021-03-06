CREATE TABLE books ( 
    id SERIAL PRIMARY KEY,
    isbn TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INTEGER NOT NULL
);

CREATE TABLE users ( 
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE reviews ( 
    id SERIAL PRIMARY KEY,
    review TEXT NOT NULL,
	user_id INTEGER NOT NULL REFERENCES users,
	book_id INTEGER NOT NULL REFERENCES books,
	rating INTEGER NOT NULL
);


