#-*-encoding=utf-8-*-
import psycopg2
from config import db_conn_config
'''
对数据库进行初始化
创建必要的表和视图
'''


table_create_command='''
CREATE SCHEMA STUMAN;

CREATE TABLE STUMAN.User(
	username char(20) PRIMARY KEY,
	password char(20),
	role char(5) CHECK(role IN ('SU','AD','SM','TM','TE','ST')),
	no char(8) CHECK (no SIMILAR TO '\\d{8}')--符合该正则表达式，即8个数字符号
);
CREATE TABLE STUMAN.Teacher(
	Tno char(8) PRIMARY KEY,
	Tname char(10),
	Tincome float(1),
	Tloc char(5) CHECK (Tloc IN ('PR','AP','LE','RE'))
	--分别为教授、副教授、讲师、研究员
);
CREATE TABLE STUMAN.Class(
	CLAno char(8) PRIMARY KEY,
	CLAmajor char(20),
	CLAgrade int,
	CLAid int,
	CLAtno char(8),
	FOREIGN KEY (CLAtno) REFERENCES STUMAN.Teacher(Tno)
);
CREATE TABLE STUMAN.Student(
	Sno char(8) PRIMARY KEY,
	Sname char(10),
	CLAno char(8) REFERENCES STUMAN.Class(CLAno),
	Sdo char(10)
);
CREATE TABLE STUMAN.Course(
	Cno char(8) PRIMARY KEY,
	Cname char(30),
	Ccredit float(1),
	Cyear int,
	Cteam char(1) CHECK(Cteam IN ('上','下')),
	Ctno char(8) REFERENCES STUMAN.Teacher(Tno),
	Ciscom boolean
);
CREATE TABLE STUMAN.Score(
	Sno char(8) REFERENCES STUMAN.Student(Sno),
	Cno char(8) REFERENCES STUMAN.Course(Cno),
	Score float(1),
	PRIMARY KEY(Sno,Cno)
);
CREATE TABLE STUMAN.CC(
	CLAno char(8) REFERENCES STUMAN.Class(CLAno),
	Cno char(8) REFERENCES STUMAN.Course(Cno),
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

view_create_command='''
CREATE VIEW STUMAN.CLA_VIEW AS
SELECT C.CLAno,C.CLAmajor,C.CLAgrade,C.CLAid,C.CLAtno,T.Tname
FROM STUMAN.Class C,STUMAN.Teacher T
WHERE C.CLAtno=T.Tno;
--班级管理的视图


CREATE VIEW STUMAN.COU_VIEW AS
SELECT C.Cno,C.Cname,C.Ccredit,C.Cyear,C.Cteam,C.Ciscom,C.Ctno,T.Tname
FROM STUMAN.Course C,STUMAN.Teacher T
WHERE C.Ctno=T.Tno;
--课程管理的视图

CREATE VIEW STUMAN.SCO_VIEW AS 
SELECT 
	C.Cno,C.Cname,C.Ccredit,C.Cyear,C.Cteam,C.Ciscom,C.Ctno,C.Tname,
	ST.Sname,ST.Sno,ST.CLAno,
	CLA.CLAgrade,CLA.CLAmajor,CLA.CLAid
	,SC.Score
FROM STUMAN.COU_VIEW C,STUMAN.Student ST,STUMAN.Score SC,STUMAN.Class CLA
WHERE C.Cno=SC.Cno AND ST.Sno=SC.Sno;
--成绩管理的视图

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

	print('creating view...')
	cursor.execute(view_create_command)
	print('done')

	conn.commit()
	print('all done')
