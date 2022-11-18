import json
import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

# Load environment variables
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY') or 'dev'
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# If any database environment variables is not set, raise an error
if DB_HOST is None:
    raise ValueError('DB_HOST is not set')
elif DB_NAME is None:
    raise ValueError('DB_NAME is not set')
elif DB_USERNAME is None:
    raise ValueError('DB_USERNAME is not set')
elif DB_PASSWORD is None:
    raise ValueError('DB_PASSWORD is not set')

app = Flask(__name__,
            static_folder='../static',
            template_folder='../templates')
app.config['SECRET_KEY'] = FLASK_SECRET_KEY


# Connect to the database
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    return conn


# Home page
@app.route('/')
@app.route('/home')
def hello():
    return render_template('home.html', title='Home')


# Todos page
@app.route('/todos')
def todos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM todos')
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('todos.html', title='Todos', todos=todos)


# Todo page, cast the todo_id to an integer
@app.route('/todos/<int:todo_id>')
def get_todo_by_id(todo_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM todos WHERE id = {todo_id}')
    todo = cur.fetchone()
    cur.close()
    conn.close()
    return render_template(
        'todo.html',
        title=f"Todo {todo['id']}",  # type: ignore
        todo=todo)


# Update todo
@app.route('/todos/<int:todo_id>', methods=['POST'])
def update_todo_by_id(todo_id: int):
    # Content-Type must be application/json
    if request.is_json:
        body = request.get_json()
        title = body.get('title')  # type: ignore
        completed = body.get('completed')  # type: ignore

        if title is None:
            return {'message': 'title is required'}, 400

        if completed is None:
            return {'message': 'completed is required'}, 400

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            f"""UPDATE todos SET title = '{title}', completed = {completed}
                        WHERE id = {todo_id}
                    """)

        # If the todo does not exist, return a 404
        if cur.rowcount == 0:
            cur.close()
            conn.close()
            return (f'Todo with id {todo_id} not found', 404)

        conn.commit()
        # Get the updated todo from the database
        cur.execute(f'SELECT * FROM todos WHERE id = {todo_id}')
        todo = cur.fetchone()
        cur.close()
        conn.close()
        return todo or (f'Todo with id {todo_id} not found', 404)
    # if Content-Type is not application/json, return 400
    else:
        return {'message': 'request body must be JSON'}, 400


# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# see https://flask.palletsprojects.com/en/2.2.x/templating/#registering-filters
# for more information
# Registering Filter
# Check Line 4 in templates/todos.html to see how to use this filter
@app.template_filter('json_dump')
def json_dump_filter(data):
    return json.dumps(data)


if __name__ == '__main__':
    app.run(debug=True)
