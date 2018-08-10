from flask import Flask, render_template, session, redirect, url_for, request, escape ,jsonify
import MySQLdb , MySQLdb.cursors
import hashlib
import random, string
import time

app = Flask(__name__)

#------------------------------
db = MySQLdb.connect(host="localhost", user="root", passwd="", db="nog")
cur = db.cursor()
#------------------------------
dict_db = MySQLdb.connect("localhost", "root", "", "nog" , cursorclass= MySQLdb.cursors.DictCursor)
dict_cur = dict_db.cursor()

app.secret_key = 'SseXFSEFSEkeWasfaDAWDx'

def selectOne(sql):
	cur.execute(sql)
	data = cur.fetchone()
	return data[0]

def selectOneRow(sql):
	cur.execute(sql)
	data = cur.fetchone()
	return data

def selectMany(sql):
	cur.execute(sql)
	data = cur.fetchall()
	return data

def IUP(sql):
	db = MySQLdb.connect(host="localhost", user="root", passwd="", db="nog")
	cur = db.cursor()
	cur.execute(sql)
	db.commit()
	db.close()
	return 'ok'


@app.route('/')
def index():
	if 'account_id' in session:
		return redirect(url_for('dashboard'))
	else:
		return render_template("index.html")
	return render_template("index.html")

@app.route('/checkLogin', methods=['POST', 'GET'])
def checkLogin():
	if request.method == 'POST':
		username = escape(request.form['username'])
		password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()

		data = selectOneRow("""SELECT
			*
			FROM
			account
			WHERE username ='{}' and password = '{}'
					""".format(username,password))
		
		if data[0]:
			session['account_id'] = data[0]
			print(session['account_id'])
			return redirect(url_for('dashboard'))
		else:
			return redirect(url_for('index'))
	else:
		return "Error"

@app.route('/dashboard')
def dashboard():
	if 'account_id' not in session:
		return redirect(url_for('index'))
	else:
		return render_template("dashboard.html")
	return render_template("dashboard.html")

@app.route('/addStudents', methods=['POST', 'GET'])
def addStudents():
	datas = selectMany("SELECT * FROM course")
	return render_template("addstudents.html", datas = datas)

@app.route('/insertStudent', methods=['POST', 'GET'])
def insertStudent():
	if request.method == 'POST':
		name = request.form['name']
		email = request.form['email']
		gender = request.form['gender']
		course_id = request.form['course']
		year = request.form['year']
		age = request.form['age']
		address = request.form['address']
		contact = request.form['contact']
		status = request.form['status']
		postal_code = request.form['postal']
		IUP("""INSERT INTO student
						(name, email, gender, course_id, image_path, age, address, contact, status, postal_code, year)
					VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')
				""".format(name, email, gender, course_id, 'default.jpg', age, address, contact, status, postal_code, year))
		print("added")
		return "Student Added!"
	else:
		return render_template("login.html")

@app.route('/studentList', methods=['POST','GET'])
def studentList():
	datas = selectMany("""SELECT *
											FROM student
											JOIN course
											WHERE student.course_id = course.id
											""")
	return render_template("studentlist.html", datas=datas)

@app.route('/view_profile/<id>', methods=['GET'])
def view_profile(id):
	if request.method == 'GET':
		results = selectOneRow("""
							SELECT a.id,a.name,a.email,a.gender,b.course,a.image_path,a.address,a.contact,a.status,a.postal_code,b.id as course_id
							FROM student as a
							INNER JOIN course as b ON a.course_id = b.id where a.id = '{}'
							""".format(id))
		course = selectMany("SELECT * FROM course")
		return render_template("view_profile.html", results=results, course = course,id = id)
	return render_template("view_profile.html")

@app.route('/update_information', methods = ['POST'])
def update_information():
	name = request.form['name']
	email = request.form['email']
	contact = request.form['contact']
	postal = request.form['postal']
	address = request.form['address']
	status = request.form['status']
	gender = request.form['gender']
	degree_id = request.form['degree']
	user_id = request.form['id']
	IUP("""
		UPDATE student set name='{}',email='{}',gender='{}',course_id='{}',address='{}',contact='{}',status='{}',
		postal_code ='{}' where id = '{}'
			""".format(name,email,gender,degree_id,address,contact,status,postal,user_id))
	return "1"

@app.route('/generateCode')
def generateCode():
	datas = selectMany("""SELECT a.id,a.name,b.course from student as a INNER JOIN course as b ON a.course_id = b.id WHERE a.course_id = 1 """)
	sem = selectMany("SELECT * FROM sem")
	exams = selectMany("SELECT * FROM exams")
	year = selectMany("SELECT * FROM year")
	course = selectMany("SELECT * FROM course")
	return render_template("generatecode.html", datas=datas, exams=exams, sem=sem, year = year,course = course)


@app.route('/getListCourse', methods = ['POST'])
def getListCourse():
	course_id = request.form['course']
	dict_cur.execute("""SELECT a.id,a.name,b.course from student as a INNER JOIN course as b ON a.course_id = b.id WHERE a.course_id = '{}'""".format(course_id))
	student = dict_cur.fetchall()
	return jsonify(student)

@app.route('/getDefaultList' , methods= ['POST'])
def getDefaultList():
	dict_cur.execute("""SELECT a.id,a.name,b.course from student as a INNER JOIN course as b ON a.course_id = b.id """)
	defaultStudent = dict_cur.fetchall()
	return jsonify(defaultStudent)


@app.route('/generateCodeStudent', methods=['post'])
def generateCodeStudent():
	term = request.form['term']
	exam = request.form['exam']
	char = 'ABCDERFGHIJKLMNOPQRSTWXYZ';
	choice = random.SystemRandom().choice
	gen_code =''.join(choice(char) for x in range(4))
	return exam+"-"+gen_code

@app.route('/update_permit', methods = ['POST'])
def update_permit():
	semester = request.form['semister']
	exam = request.form['exam']
	permit = request.form['permit']
	idd = request.form['id']

	dict_cur.execute("""
		SELECT id from permit where student_id = '{}' and semester = '{}' and exam = '{}'
		""".format(idd,semester,exam))
	data = dict_cur.fetchone()
	if data is None:
		dict_cur.execute( """
				INSERT INTO permit(student_id,semester,exam,permit) VALUES('{}','{}','{}','{}')
	 		""".format(idd,semester,exam,permit))
		dict_db.commit()
		print("done")
		return "done"
	else:
		print("already exist")
		return 'already exist'




@app.route('/aa')
def aa():
	dict_cur.execute("""
		SELECT id,permit FROM permit
		""")
	data = dict_cur.fetchall()
	return jsonify(data)


@app.route('/student_permit', methods = ['POST'])
def student_permit():
	idd = request.form['id']
	dict_cur.execute("""
		SELECT * FROM permit where student_id = '{}'
		""".format(idd))
	data = dict_cur.fetchall()
	return jsonify(data)

@app.route('/permit')
def permit():
	dict_cur.execute("""SELECT * FROM permit""")
	data = dict_cur.fetchall()
	return jsonify(data)

@app.route('/get_permit', methods = ['POST'])
def get_permit():
	idd = request.form['id']
	semester = request.form['term']
	exam = request.form['exam']

	dict_cur.execute("""
		SELECT permit FROM permit where student_id = '{}' and semester = '{}' and exam = '{}'
		""".format(idd,semester,exam))
	data = dict_cur.fetchall()
	return jsonify(data)


@app.route('/logout')
def logout():
	session.pop('account_id', None)
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)
