#!/bin/env python

from Queue import Queue

import MySQLdb
import threading
import multiprocessing
import random
import time  



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
TEST_DATA_COUNT=1000
TEST_EXEC_COUNT=1000

class ThreadPool:
    def __init__(self,n):
        self.thread_objects = []
        self.num = n
        
    def assign(self, consmer_obj):
        self.thread_objects.append(consmer_obj)
            
    def start(self):
        for thread_object in self.thread_objects:
            thread_object.start()
#             print "%s started" % thread_object
            
    def join(self):
        for thread_object in self.thread_objects:
            thread_object.join()
#             print "%s joined" % thread_object
            
    def stop(self):
        for thread_object in self.thread_objects:
            thread_object.stop()
#             print "%s stopped" % thread_object
            
    def thread_pool_length(self):
        return len(self.thread_objects)

#Producer thread  
  
class Producer(threading.Thread):
  
    def __init__(self, t_name, queue):  
  
        threading.Thread.__init__(self, name=t_name)  
  
        self.data=queue  
  
    def run(self):  
  
        for i in range(TEST_EXEC_COUNT):  
  
#             print "%s: %s is producing %d to the queue!\n" %(time.ctime(), self.getName(), i)  
  
            self.data.put(random.randint(0,TEST_DATA_COUNT*2))
  
            time.sleep(0.1)
  
        print "%s: %s finished!" %(time.ctime(), self.getName())
        
    def stop(self):
        for i in range(THREAD_COUNT):  
            self.data.put("quit")
            
        print "send quit signal to notify the worker quit!"
        
        
class Consumer(threading.Thread):  
  
    def __init__(self, t_name, queue):
  
        threading.Thread.__init__(self, name=t_name)  
  
        self.data=queue
        
        self.stop_status = False
  
    def run(self):  
  
        while(not self.stop_status):
  
            val = self.data.get()
            
            if "quit" == val:
                break
  
            try:
                con=MySQLdb.connect(host=HOST,user=USER,passwd=PASSWORD,port=PORT,db=TEST_DB)
            except Exception, e:
                print e
                
                if con is not None:
                    con.close()
                    
                continue
            
            try:
                cursor=con.cursor()
                sql=QUERY_SQL%val
                cursor.execute(sql)
            except Exception, e:
                print e
            finally:
                if cursor is not None:
                    cursor.close()
    
                if con is not None:
                    con.close()
                    
            print "%s: %s is consuming. %d in the queue is consumed!" %(time.ctime(), self.getName(), val)
  
#             time.sleep(random.randrange(10))
  
        print "%s: %s finished!" %(time.ctime(), self.getName())
        
    def stop(self):
        self.stop_status = True
        
#Main thread  
  
def main():  
  
    queue = Queue()
  
    producer = Producer('Pro.', queue)
    producer.start()
    
    
    tp = ThreadPool(THREAD_COUNT)
    for i in range(THREAD_COUNT):
#         print "thread pool length:%s" % tp.thread_pool_length()
        consumer = Consumer('Con.%s' % i, queue)
        tp.assign(consumer)
    
    tp.start()
  
    producer.join()
    print "producer push data finished"
    
    time.sleep(20)
    
    tp.stop()
    producer.stop()
    
    tp.join()
    print "consumers quit! (*10)"
    
    print 'All threads terminate!'
  
   
  
def prepare_test_data():
    con=MySQLdb.connect(host=HOST,user=USER,passwd=PASSWORD,port=PORT)
    assert con
    cursor=con.cursor()
    cursor.execute(CHECK_SQL)
    cursor.execute(CREATE_DB_SQL)
    con.select_db(TEST_DB)
    cursor.execute(CREATE_TABLE_SQL)
    cursor.close()
    
    for i in range(TEST_DATA_COUNT):
        sql=INSERT_SQL%(i+1,random.randint(0,TEST_DATA_COUNT))
        cursor=con.cursor()
        cursor.execute(sql)
        cursor.close()
        con.commit()
        
    print "create test data ok"
    con.close()
    
def run_test_by_processor():
    pool=multiprocessing.Pool()
    for i in range(PROCESS_COUNT):
        pool.apply_async(stress_test)
    pool.close()
    pool.join()
 
if __name__=="__main__":
    main()
