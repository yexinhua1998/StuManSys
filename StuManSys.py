#-*-encoding=utf-8-*-

import web
from file import files,file_name
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

	'/ad_teacher_management','ad_teacher_management',
	'/ad_add_teacher','ad_add_teacher',
	'/ad_delete_teacher','ad_delete_teacher',
	'/ad_update_teacher','ad_update_teacher',

	'/tm_course_management','tm_course_management',
	'/tm_add_course','tm_add_course',
	'/tm_delete_course','tm_delete_course',
	'/tm_update_course','tm_update_course',

	'/st_score_query','st_score_query',
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
	initializer={'username':None,'role':None,'no':None})

class index:
	def GET(self):
		return files['login']

class file_get:
	def GET(self,path):
		try:
			return files[file_name[path]]
		except:
			return files['abandoned']

class verification:
	def POST(self):
		input=web.input()
		result=db.query('SELECT * FROM STUMAN.User WHERE username=\'%s\';'%input.username).list()
		if len(result)==0:
			return files['user_not_exist']
		else:
			real_pw=result[0]['password'].strip()
			role=result[0]['role'].strip()
			no=result[0]['no'].strip()
			print(real_pw)
			if real_pw==input.password:
				session.username=input.username
				session.role=role
				session.no=no
				raise web.seeother('/'+session.role)
			else:
				return files['password_incorrect']


def role_check(input_role,target_role_list):
	if input_role in target_role_list:
		return
	else:
		print('role check failed')
		print('session:')
		print(session)
		raise web.seeother('/abandoned')

class abandoned:
	def GET(self):
		print('abandoned')
		return files['abandoned']

class student:
	def GET(self):
		role_check(session.role,['ST'])
		return render.student(session.username,session.no)

class teacher:
	def GET(self):
		role_check(session.role,['TE'])
		return render.teacher(session.username,session.no)

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

##########################下面为功能部分#############################


######行政部分######
class ad_teacher_management:
	def GET(self):
		role_check(session.role,['AD'])
		data=db.query('SELECT * FROM STUMAN.Teacher').list()
		return render.ad_teacher_management(session.username,data)

class ad_add_teacher:
	#增加老师的部分
	def POST(self):
		role_check(session.role,['AD'])
		data=web.input()
		command="INSERT INTO STUMAN.Teacher VALUES('%s','%s',%s,'%s')"\
		%(data.tno,data.tname,data.tincome,data.tloc)
		try:
			db.query(command)
			return render.operation_result('ad_teacher_management',None)
		except Exception as e:
			return render.ad_add_teacher('ad_teacher_management',e)

class ad_delete_teacher:
	#删除老师
	def POST(self):
		role_check(session.role,['AD'])
		data=web.input()
		command="DELETE FROM STUMAN.Teacher WHERE Tno='%s'"%data.tno
		try:
			db.query(command)
			return render.operation_result('ad_teacher_management',None)
		except Exception as e:
			return render.operation_result('ad_teacher_management',e)

class ad_update_teacher:
	#修改老师
	def POST(self):
		role_check(session.role,['AD'])
		data=web.input()
		command="UPDATE STUMAN.Teacher SET Tname='%s',Tincome=%s,Tloc='%s' WHERE Tno='%s'"\
		%(data.tname,data.tincome,data.tloc,data.tno)
		try:
			db.query(command)
			return render.operation_result('ad_teacher_management',None)
		except Exception as e:
			return render.operation_result('ad_teacher_management',e)

######教务处部分######
class tm_course_management:
	def GET(self):
		role_check(session.role,['TM'])
		command="SELECT * FROM STUMAN.COU_VIEW;"
		data=db.query(command).list()
		return render.tm_course_management(session.username,data)


class tm_add_course:
	def POST(self):
		role_check(session.role,['TM'])
		data=web.input(ciscom=[])
		ciscom='True' if len(data.ciscom)==1 else 'False'
		command="INSERT INTO STUMAN.Course VALUES('%s','%s',%s,%s,'%s','%s',%s)"\
		%(data.cno,data.cname,data.ccredit,data.cyear,data.cteam,data.ctno,ciscom)
		try:
			db.query(command)
			return render.operation_result('tm_course_management',None)
		except Exception as e:
			return render.operation_result('tm_course_management',e)


class tm_delete_course:
	#删除课程的类
	def POST(self):
		role_check(session.role,['TM'])
		data=web.input()
		command="DELETE FROM STUMAN.Course WHERE cno='%s'"%data.cno 
		try:
			db.query(command)
			return render.operation_result('/tm_course_management',None)
		except Exception as e:
			return render.operation_result('/tm_course_management',e)

class tm_update_course:
	#更新课程的类
	def POST(self):
		role_check(session.role,['TM'])
		data=web.input(ciscom=[])
		ciscom='True' if len(data.ciscom)==1 else 'False'
		command="UPDATE STUMAN.Course SET \
		Cname='%s',Ccredit=%s,Cyear=%s,Cteam='%s',Ctno='%s',Ciscom=%s WHERE Cno='%s'"\
		%(data.cname,data.ccredit,data.cyear,data.cteam,data.ctno,ciscom,data.cno)
		try:
			db.query(command)
			return render.operation_result('tm_course_management',None)
		except Exception as e:
			return render.operation_result('tm_course_management',e)

class st_score_query:
	'''
	学生的成绩查询功能
	'''
	def GET(self):
		role_check(session.role,['ST'])
		command='''
		SELECT Cno,Cname,Ccredit,Cyear,Cteam,Ciscom,Ctno,Tname,Score
		FROM STUMAN.SCO_VIEW
		WHERE Sno=%s;
		'''
		data=db.query(command%session.no)
		return 

if __name__=='__main__':
	app.run()