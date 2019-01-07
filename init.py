#-*-encoding=utf-8-*-
import psycopg2
from config import db_conn_config
'''
对数据库进行初始化
创建必要的表和视图
'''


table_create_command='''
CREATE SCHEMA STUMAN;

CREATE TABLE STUMAN.Teacher(
	Tno Serial PRIMARY KEY,
	Tname char(10),
	Tincome float(1),
	Tloc char(10) CHECK (Tloc IN ('教授','副教授','讲师','研究员'))
);
CREATE TABLE STUMAN.Class(
	CLAno Serial PRIMARY KEY,
	CLAmajor char(20),
	CLAgrade int,
	CLAid int,
	CLAtno int,
	FOREIGN KEY (CLAtno) REFERENCES STUMAN.Teacher(Tno)
);
CREATE TABLE STUMAN.Student(
	Sno char(8) PRIMARY KEY,
	Sname char(10),
	CLAno int REFERENCES STUMAN.Class(CLAno),
	Sdo char(10)
);
CREATE TABLE STUMAN.Course(
	Cno serial PRIMARY KEY,
	Cname char(30),
	Ccredit float(1),
	Cyear int,
	Cteam char(1) CHECK(Cteam IN ('上','下')),
	Ctno int REFERENCES STUMAN.Teacher(Tno),
	Ciscom boolean
);
CREATE TABLE STUMAN.Score(
	Sno char(8) REFERENCES STUMAN.Student(Sno),
	Cno int REFERENCES STUMAN.Course(Cno),
	Score float(1),
	PRIMARY KEY(Sno,Cno)
);
CREATE TABLE STUMAN.CC(
	CLAno int REFERENCES STUMAN.Class(CLAno),
	Cno int REFERENCES STUMAN.Course(Cno),
	PRIMARY KEY (CLAno,Cno)
);
'''

index_create_command='''

CREATE INDEX tea_tname ON STUMAN.Teacher USING HASH(Tname);
CREATE INDEX tea_tloc ON STUMAN.Teacher USING HASH(Tloc);
CREATE INDEX tea_tincome ON STUMAN.Teacher(Tincome);

CREATE INDEX stu_clano ON STUMAN.Student USING HASH(CLAno);

CREATE INDEX cla_clamajor ON STUMAN.Class USING HASH(CLAmajor);
CREATE INDEX cla_clagrade ON STUMAN.Class(CLAgrade);
CREATE INDEX cla_clatno ON STUMAN.Class USING HASH(CLAtno);

CREATE INDEX cou_cname ON STUMAN.Course(Cname);
CREATE INDEX cou_cyear ON STUMAN.Course(Cyear);
CREATE INDEX cou_ciscom ON STUMAN.Course USING HASH(Ciscom);
CREATE INDEX cou_ctno ON STUMAN.Course USING HASH(Ctno);

CREATE INDEX sco_sno ON STUMAN.Score(Sno);
CREATE INDEX sco_cno ON STUMAN.Score USING HASH(Cno);
CREATE INDEX sco_sco ON STUMAN.Score(Score);

CREATE INDEX cc_clano ON STUMAN.CC USING HASH(CLAno);
CREATE INDEX cc_cno ON STUMAN.CC USING HASH(Cno);

'''

if __name__=='__main__':
	print('connecting database...')
	conn=psycopg2.connect(**db_conn_config())
	print('done.')

	cursor=conn.cursor()

	print('creating table...')
	cursor.execute(table_create_command)
	print('done')

	print('creating index...')
	cursor.execute(index_create_command)
	print('done')

	conn.commit()
	print('all done')
