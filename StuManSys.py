#-*-encoding=utf-8-*-

import web
from file import files,file_name
import psycopg2
import config

urls=(
	'/','index',
	'/verification','verification',
	'/(.+)','file_get'
)

db_conn=psycopg2.connect(**config.db_conn_config())

class index:
	def GET(self):
		return files['login']

class verification:
	def POST(self):
		print('verification')
		input=web.input()
		cursor=db_conn.cursor()
		command='SELECT * FROM STUMAN.User WHERE username=\'%s\';'%input.username
		cursor.execute(command)
		if cursor.rowcount==0:
			return files['user_not_exist']
		else:
			result=cursor.fetchall()[0]
			print(result)
			_,real_pw,role=result
			real_pw=real_pw.strip()
			role=role.strip()
			if real_pw==input.password:
				return files['verification_success']
			else:
				return files['password_incorrect']

class file_get:
	def GET(self,path):
		print('fileget')
		print('path=%s'%(path))
		return files[file_name[path]]

app=web.application(urls,globals())

if __name__=='__main__':
	app.run()