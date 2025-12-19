from flask import Flask, g, request, jsonify
import sqlite3
import logging
import os

app = Flask(__name__)

DATABASE = 'database.db'

sql_logger = logging.getLogger('sql_logger')
sql_logger.setLevel(logging.DEBUG)

if not sql_logger.handlers:
    file_handler = logging.FileHandler('sql.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    sql_logger.addHandler(file_handler)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    sql_logger.addHandler(console_handler)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.set_trace_callback(sql_logger.debug)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO users (name, age) VALUES (?, ?)",
                [('Саша', 25), ('Ваня', 30), ('Костя', 35)]
            )
        db.commit()

@app.route('/users')
def get_users():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify([{'id': u[0], 'name': u[1], 'age': u[2]} for u in users])

@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    age = data.get('age')
    if not name or age is None:
        return jsonify({'error': 'Invalid data'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
    db.commit()
    return jsonify({'message': 'User added', 'id': cursor.lastrowid})

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)