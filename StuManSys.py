#-*-encoding=utf-8-*-

import web
from file import files,file_name

urls=(
	'/','index',
	'/(.+)','file_get'
)

class index:
	def GET(self):
		return files['login']

class file_get:
	def GET(self,path):
		print('path=%s'%(path))
		return files[file_name[path]]

app=web.application(urls,globals())

if __name__=='__main__':
	app.run()