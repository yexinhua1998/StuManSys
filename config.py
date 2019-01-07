#-*-encoding=utf-8-*-
'''
配置文件
'''

def db_conn_config():

	#数据库连接的配置

	config={
		'host':'localhost',
		'user':'postgres',
		'password':'admin',
		'dbname':'design',
		'port':5432
	}
	
	return config