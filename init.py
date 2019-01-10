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
	Tno char(8) PRIMARY KEY CHECK(Tno SIMILAR TO '\\d{8}'),
	Tname char(10),
	Tincome float(1),
	Tloc char(5) CHECK (Tloc IN ('PR','AP','LE','RE'))
	--分别为教授、副教授、讲师、研究员
);
CREATE TABLE STUMAN.Class(
	CLAno char(8) PRIMARY KEY CHECK(CLAno SIMILAR TO '\\d{8}'),
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
	Cno char(8) PRIMARY KEY CHECK (Cno SIMILAR TO '\\d{8}'),
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
--班级管理的视图
SELECT C.CLAno,C.CLAmajor,C.CLAgrade,C.CLAid,C.CLAtno,T.Tname
FROM STUMAN.Class C,STUMAN.Teacher T
WHERE C.CLAtno=T.Tno;


CREATE VIEW STUMAN.COU_VIEW AS
--课程管理的视图
SELECT C.Cno,C.Cname,C.Ccredit,C.Cyear,C.Cteam,C.Ciscom,C.Ctno,T.Tname
FROM STUMAN.Course C,STUMAN.Teacher T
WHERE C.Ctno=T.Tno;

CREATE VIEW STUMAN.SCO_VIEW AS 
--成绩管理的视图
SELECT 
	C.Cno,C.Cname,C.Ccredit,C.Cyear,C.Cteam,C.Ciscom,C.Ctno,C.Tname,
	ST.Sname,ST.Sno,ST.CLAno,
	CLA.CLAgrade,CLA.CLAmajor,CLA.CLAid
	,SC.Score
FROM STUMAN.COU_VIEW C,STUMAN.Student ST,STUMAN.Score SC,STUMAN.Class CLA
WHERE C.Cno=SC.Cno AND ST.Sno=SC.Sno AND ST.CLAno=CLA.CLAno;

CREATE VIEW STUMAN.CC_VIEW AS 
--必修管理的视图
SELECT CLA.CLAno,CLA.CLAgrade,CLA.CLAmajor,CLA.CLAid,C.Cname,C.Cno
FROM STUMAN.Class CLA,STUMAN.Course C,STUMAN.CC CC 
WHERE CLA.CLAno=CC.CLAno AND C.Cno=CC.Cno;

CREATE VIEW STUMAN.score_statistic_view AS 
--按班级和科目统计成绩的视图
SELECT C.Cno,C.Cname,C.Cyear,C.Cteam,C.Ctno,CLA.CLAno,CLA.CLAgrade,CLA.CLAmajor,CLA.CLAid,
	AVG(SCO.Score),MAX(SCO.Score),MIN(SCO.Score),get_pass_ratio(CLA.CLAno,C.Cno)
FROM STUMAN.Course C,STUMAN.Class CLA,STUMAN.Score SCO,STUMAN.Student STU
WHERE SCO.Cno=C.Cno AND SCO.Sno=STU.Sno AND STU.CLAno=CLA.CLAno
GROUP BY(C.Cno,CLA.CLAno);

CREATE VIEW STUMAN.score_statistic_outer_view AS 
--对用户显示统计结果的视图
SELECT cno,cname,cyear,cteam,ctno,clano,clagrade,clamajor,claid,avg,max,min,get_pass_ratio,T.tname
FROM STUMAN.score_statistic_view,STUMAN.Teacher T
WHERE T.tno=ctno;
'''

function_create_command='''
CREATE FUNCTION select_course(input_sno char(8),input_cno char(8)) RETURNS boolean
--学生选课函数
AS $$
DECLARE
	exist_course boolean;
	is_com boolean;
	have_selected boolean;
BEGIN
	SELECT exists(SELECT * FROM STUMAN.Score WHERE sno=input_sno AND cno=input_cno) INTO have_selected;
	IF have_selected THEN
		RAISE '已选修该课程';
	END IF;

	SELECT EXISTS(SELECT * FROM STUMAN.Course C WHERE C.cno=input_cno) INTO exist_course;
	IF exist_course IS FALSE THEN
		RAISE '课程不存在';
	END IF;

	SELECT ciscom FROM STUMAN.Course C WHERE C.cno=input_cno INTO is_com;
	IF is_com THEN
		RAISE '该课程不是选修课程';
	END IF;

	INSERT INTO STUMAN.Score VALUES(input_sno,input_cno,NULL);
	RETURN True;
END;
$$
LANGUAGE plpgsql;

CREATE FUNCTION class_insert_course(iclano char(8),icno char(8)) RETURNS boolean
--为班级插入必修课时的函数
AS $$
DECLARE
	exists_course boolean;
	is_com boolean;
	exists_cc boolean;
BEGIN
	--检查是否存在该课
	SELECT EXISTS(SELECT * FROM STUMAN.Course WHERE icno=cno) INTO exists_course;
	IF exists_course IS FALSE THEN
		RAISE '不存在该课';
	END IF;

	--检查该课是否为必修
	SELECT ciscom FROM STUMAN.Course WHERE icno=cno INTO is_com;
	IF is_com IS FALSE THEN
		RAISE '该课为选修课';
	END IF;

	--检查该班级是否已经必修该课
	SELECT EXISTS(SELECT * FROM STUMAN.CC WHERE clano=iclano AND icno=cno) INTO exists_cc;
	IF exists_cc THEN 
		RAISE '该班级已经必修该课';
	END IF; 

	--执行插入
	INSERT INTO STUMAN.CC VALUES(iclano,icno);
	INSERT INTO STUMAN.Score
	SELECT STU.Sno,icno Cno,NULL Score FROM STUMAN.Student STU
	WHERE STU.CLAno=iclano;
	RETURN TRUE;
END;
$$
LANGUAGE plpgsql;

CREATE FUNCTION CLASS_DELETE_COURSE(iclano char(8),icno char(8)) RETURNS boolean
--从班级中删除必修课
AS $$
DECLARE
	exists_rel boolean;--是否存在该关系
BEGIN
	SELECT EXISTS(SELECT * FROM STUMAN.CC WHERE CLAno=iclano AND Cno=icno) INTO exists_rel;
	IF exists_rel IS FALSE THEN
		RAISE '该班级不存在或该课程不存在或该班级未必修该课程，请检查。';
	END IF;

	DELETE FROM STUMAN.CC WHERE clano=iclano AND cno=icno;
	DELETE FROM STUMAN.Score WHERE sno IN (
		SELECT sno FROM STUMAN.Student WHERE clano=iclano
	)AND cno=icno;
	RETURN True;
END;
$$
LANGUAGE plpgsql;

CREATE FUNCTION teacher_update_score(itno char(8),icno char(8),isno char(8),iscore float(1)) RETURNS boolean
--教师修改学生成绩的函数
AS $$
DECLARE
	is_teach_this boolean;--该教师是否教这门课
	is_stu_take boolean;--该学生是否上这门课
BEGIN
	--检查该教师是否教这门课
	SELECT EXISTS(SELECT * FROM STUMAN.Course WHERE cno=icno AND ctno=itno) INTO is_teach_this;
	IF is_teach_this IS FALSE THEN
		RAISE '您没有教授这门课';
	END IF;

	--检查该学生是否上这门课
	SELECT EXISTS(SELECT * FROM STUMAN.Score WHERE cno=icno AND sno=isno) INTO is_stu_take;
	IF is_stu_take IS FALSE THEN 
		RAISE '该学生没有上这门课';
	END IF;

	--修改
	UPDATE STUMAN.Score SET Score=iscore WHERE icno=cno AND isno=sno;

	RETURN True;
END;
$$
LANGUAGE plpgsql;

CREATE FUNCTION CREATE_USER(role char(5),no char(8)) RETURNS boolean
AS $$
BEGIN
	IF role='ST' THEN
		INSERT INTO STUMAN.User VALUES('S'||no,'123456','ST',no);
		RETURN True;
	END IF;

	IF role='TE' THEN
		INSERT INTO STUMAN.User VALUES('T'||no,'123456','TE',no);
		RETURN True;
	END IF;

	RAISE '不支持的角色';
END;
$$
LANGUAGE plpgsql;

CREATE FUNCTION get_pass_ratio(iclano char(8),icno char(8)) RETURNS float(2)
--计算通过率的函数
AS $$
DECLARE
	pass_num numeric;
	total_num numeric;
BEGIN
	SELECT COUNT(*) FROM STUMAN.Student STU,STUMAN.Score SCO 
	WHERE STU.Sno=SCO.Sno AND STU.CLAno=iclano AND SCO.Cno=icno AND SCO.Score IS NOT NULL 
	INTO total_num;
	IF total_num IS NULL OR total_num=0 THEN 
		RETURN NULL;
	END IF;

	SELECT COUNT(*) FROM STUMAN.Student STU,STUMAN.Score SCO 
	WHERE STU.Sno=SCO.Sno AND STU.CLAno=iclano AND SCO.Cno=icno AND SCO.Score>=60
	INTO pass_num;

	RETURN (pass_num/total_num)*100;
END;
$$
LANGUAGE plpgsql;

CREATE FUNCTION create_student_user() RETURNS trigger 
AS $$
--为新插入的学生创建用户
BEGIN
	IF OLD IS NULL THEN
		--插入时，为新学生创建新的用户
		INSERT INTO STUMAN.User VALUES('S'||new.Sno,'123456','ST',new.Sno);
		RETURN new;
	ELSE
		--删除时，为学生删除用户
		DELETE FROM STUMAN.User WHERE username='S'||old.Sno;
		RETURN old;
	END IF;
END;
$$
LANGUAGE plpgsql;

CREATE trigger create_student_user AFTER INSERT OR DELETE ON STUMAN.Student 
	FOR EACH ROW EXECUTE PROCEDURE create_student_user();

CREATE FUNCTION create_teacher_user() RETURNS trigger
AS $$
BEGIN
	IF old IS NULL THEN
		--新增老师，应该为他分配用户
		INSERT INTO STUMAN.User VALUES('T'||new.tno,'123456','TE',new.tno);
		RETURN old;
	ELSE
		--删除老师，应该将其用户删除
		DELETE FROM STUMAN.User WHERE username='T'||old.tno;
		RETURN old;
	END IF;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER create_teacher_user AFTER INSERT OR DELETE ON STUMAN.Teacher 
	FOR EACH ROW EXECUTE PROCEDURE create_teacher_user();
'''

insert_command='''
INSERT INTO STUMAN.User VALUES('AD','AD','AD','00000000');
INSERT INTO STUMAN.User VALUES('TM','TM','TM','00000000');
INSERT INTO STUMAN.User VALUES('SM','SM','SM','00000000');
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

	print('creating function...')
	cursor.execute(function_create_command)
	print('done')

	print('creating view...')
	cursor.execute(view_create_command)
	print('done')

	print('inserting raw data...')
	cursor.execute(insert_command)
	print('done')

	conn.commit()
	print('commited')
	print('all done')
