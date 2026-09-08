from app import app 

from flask import render_template, request, url_for

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    return 'p'

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')