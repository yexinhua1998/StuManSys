#-*-encoding=utf-8-*-

import web
from file import files,file_name
import psycopg2
import config

web.config.debug=False

urls=(
	'/','index',
	'/verification','verification',
	'/main','main',
	'/ST','student',
	'/TE','teacher',
	'/AD','administrator',
	'/SM','student_management',
	'/TM','teaching_management',
	'/logout','logout',
	'/abandoned','abandoned',
	'/(.+)','file_get'
)

db=web.database(dbn='postgres',**config.db_conn_config())

render=web.template.render('html/')

role_showed={
	'SU':'超级用户',
	'AD':'行政人员',
	'SM':'学生管理人员',
	'TM':'教学管理人员',
	'TE':'教师',
	'ST':'学生'
}

app=web.application(urls,globals())

session=web.session.Session(app,web.session.DiskStore('sessions'),
	initializer={'username':None,'role':None})

class index:
	def GET(self):
		return files['login']

class file_get:
	def GET(self,path):
		return files[file_name[path]]

class verification:
	def POST(self):
		input=web.input()
		result=db.query('SELECT * FROM STUMAN.User WHERE username=\'%s\';'%input.username).list()
		if len(result)==0:
			return files['user_not_exist']
		else:
			real_pw=result[0]['password'].strip()
			role=result[0]['role'].strip()
			print(real_pw)
			if real_pw==input.password:
				session.username=input.username
				session.role=role
				raise web.seeother('/'+session.role)
			else:
				return files['password_incorrect']

class main:
	def GET(self):
		return render.main(session.role,role_showed[session.role])

def role_check(input_role,target_role_list):
	if input_role in target_role_list:
		return
	else:
		raise web.seeother('/abandoned')

class abandoned:
	def GET(self):
		return files['abandoned']

class student:
	def GET(self):
		role_check(session.role,['ST'])
		return render.student(session.username)

class teacher:
	def GET(self):
		role_check(session.role,['TE'])
		return render.teacher(session.username)

class administrator:
	def GET(self):
		role_check(session.role,['AD'])
		return render.administrator(session.username)

class student_management:
	def GET(self):
		role_check(session.role,['SM'])
		return render.student_management(session.username)

class teaching_management:
	def GET(self):
		role_check(session.role,['TM'])
		return render.teaching_management(session.username)

class logout:
	def GET(self):
		session.kill()
		raise web.seeother('/')

class score_query:
	def GET(self):
		if session.role != 'ST':
			return files['abandoned']
		return ''

if __name__=='__main__':
	app.run()