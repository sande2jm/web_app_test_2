from app import app
from flask import render_template, flash, redirect, url_for
import pymysql
import datetime
from flask import request

rds_host  = 'test.cn1xyxm7ffae.us-east-1.rds.amazonaws.com'
name = 'master'
password = 'password'
db_name = 'test'

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except:
    print("ERROR: Unexpected error: Could not connect to MySql instance.")

print("Connected to Test RDS_DB")

def get_movies():
	with conn.cursor() as cur:
		cur.execute(f'select * from Movies')
	res = cur.fetchall()
	return res

def get_times(title):
	with conn.cursor() as cur:
		cur.execute(f'select time from Tickets where title = "{title}"')
	res = cur.fetchall()
	return res	

@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html")

@app.route('/select')
def select():
	# theatre = request.args.get('theatre')
	# row = request.args.get('row')
	# col = request.args.get('col')
	# print(row,col)
	return render_template("select.html")

@app.route('/favicon.ico')
def hello():
    return redirect(url_for('static', filename='favicon.ico'), code=302)

def display_seats(title, time):
	rows = 5
	cols = 10
	print(title, time)
	with conn.cursor() as cur:
		cur.execute(f'select * from Tickets where title = "{title}" and time = "{time}"')
		res = cur.fetchall()
	theatre = []
	for row in range(rows):
		theatre.append([None]*cols)
	for elem in res:
		title, time,row, col, reserved = elem
		theatre[row][col] = reserved
	return theatre


@app.route('/booth')
def booth():
	title = request.args.get('movie')
	time = request.args.get('time')

	theatre = display_seats(title, time)
	for row in theatre:
		print(row)

	return render_template("booth.html", theatre=theatre)

@app.route('/movies')
def movies():
	movies = get_movies()
	movies = list(map(list, list(movies)))
	movies = list(map("".join, movies))
	print(movies)
	d = []
	for movie in movies:
		times = get_times(movie)
		times = [x[0] for x in times]
		print(times[0], type(times[0]), len(times), len(set(times)))
		times = set(times)
		times = list(map(str, times))
		times.sort()
		d.append({'title':movie, 'times': times})
		print(d)

	return render_template("movies.html", info=d)
