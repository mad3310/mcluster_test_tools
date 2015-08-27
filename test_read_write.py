#!/bin/env python
import MySQLdb
import threading
import multiprocessing
import random



NEED_INIT_TEST_DATA=False
TEST_DB="xsank"
TEST_TABLE="test_num"
HOST="127.0.0.1"
USER="zbz"
PASSWORD="zbz"
PORT=3306
CHECK_SQL="drop database if exists %s" % TEST_DB
CREATE_DB_SQL="create database %s" % TEST_DB
CREATE_TABLE_SQL="create table %s(id int,num int)" % TEST_TABLE
INSERT_SQL="insert into test_num values (%s,%s)"
QUERY_SQL="select * from test_num where num=%s"
PROCESS_COUNT=10
THREAD_COUNT=10
TEST_DATA_COUNT=1000000
TEST_EXEC_COUNT=1000000
 
class ThreadPool:
    def __init__(self,n):
        self.threads=[]
        self.num=n
        
    def assign(self,work):
        for i in range(self.num):
            self.threads.append(threading.Thread(target=work))
            
    def start(self):
        for thread in self.threads:
            thread.start()
            
        for thread in self.threads:
            thread.join
 
def stress_test():
    count=TEST_EXEC_COUNT
    con = None
    cursor = None
    while count:
        try:
            con=MySQLdb.connect(host=HOST,user=USER,passwd=PASSWORD,port=PORT,db=TEST_DB)
        except Exception, e:
            print e
            
            if con is not None:
                con.close()
                
            continue
        
        try:
            print "create connection success,%s%s" % (threading.current_thread(),str(count))
            cursor=con.cursor()
            sql=QUERY_SQL%random.randint(0,TEST_DATA_COUNT*2)
            cursor.execute(sql)
        except Exception, e:
            print e
        finally:
            if cursor is not None:
                cursor.close()

            if con is not None:
                con.close()
                
            count-=1

def create_test():
    con=MySQLdb.connect(host=HOST,user=USER,passwd=PASSWORD,port=PORT)
    assert con
    cursor=con.cursor()
    cursor.execute(CHECK_SQL)
    cursor.execute(CREATE_DB_SQL)
    con.select_db(TEST_DB)
    cursor.execute(CREATE_TABLE_SQL)
    for i in range(TEST_DATA_COUNT):
        sql=INSERT_SQL%(i+1,random.randint(0,TEST_DATA_COUNT))
        cursor.execute(sql)
    print "create test data ok"
    cursor.close()
    con.commit()
    con.close()
    
def process_run_test():
    pool=multiprocessing.Pool()
    for i in range(PROCESS_COUNT):
        pool.apply_async(stress_test)
    pool.close()
    pool.join()
 
if __name__=="__main__":
    tp=ThreadPool(THREAD_COUNT)
    tp.assign(stress_test)
    tp.start()