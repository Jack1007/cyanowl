from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relation
from datetime import datetime
from xml.dom import minidom
import redis
import traceback
import threading
import time
import os

from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWD, DB_NAME, RDB_HOST, RDB_PORT, TCPPORT_DB, UDPPORT_DB, OFFTCPPORT_DB, OFFUDPPORT_DB

TCPPORT_REDIS_POOL = redis.ConnectionPool(host = RDB_HOST, port = RDB_PORT, db = TCPPORT_DB)
UDPPORT_REDIS_POOL = redis.ConnectionPool(host = RDB_HOST, port = RDB_PORT, db = UDPPORT_DB)
OFFTCPPORT_REDIS_POOL = redis.ConnectionPool(host = RDB_HOST, port = RDB_PORT, db = OFFTCPPORT_DB)
OFFUDPPORT_REDIS_POOL = redis.ConnectionPool(host = RDB_HOST, port = RDB_PORT, db = OFFUDPPORT_DB)

WARN_TIME = 150

db_scheme = "mysql://{0}:{1}@{2}:{3}/{4}?charset=utf8".format(DB_USER, DB_PASSWD, DB_HOST, DB_PORT, DB_NAME)

Base = declarative_base()

#redis_connections = {}
#sessions = {}
dblock = threading.Lock()
msglock = threading.Lock()

def nowtime():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def strtotime(timestr, time_format):
    return datetime.strptime(timestr,time_format)

class UniqException(Exception):
    pass

class PortMonit(Base):
    __tablename__ = "portmonit"

    id = Column(Integer, primary_key = True)
    ip = Column(String(15), nullable = False)
    port = Column(Integer, nullable = False)
    prot_type = Column(String(10), nullable = False)
    reported = Column(Integer, nullable = False, default=1)
    updatetime = Column(DateTime, nullable = True, default = nowtime, onupdate = nowtime)

    def __init__(self, ip, port, prot_type, reported):
        self.ip = ip
        self.port = port
        self.prot_type = prot_type
        self.reported = reported
    def __repr__(self):
        return "<PortMonit('{0}', '{1}', '{2}')>".format(self.ip, self.port, self.prot_type)





class UserTest(Base):
    __tablename__ = "usertest"
    id = Column(Integer, primary_key = True)
    username = Column(String(30), nullable = False)

    def __init__(self, username):
        self.username = username
    def __repr__(self):
        return "<UserTest('{0}')>".format(self.username)

init_engine = create_engine(db_scheme)
Base.metadata.create_all(init_engine)

#class CreateSession(object):
#    def create_session(self):
#        str_pid = str(os.getpid())
#        if str_pid not in sessions:
#            engine = create_engine(db_scheme)
#            Session = sessionmaker(bind = engine)
#            sessions[str_pid] = Session()
#            return sessions
#        else:
#            return sessions


class CreateSession(object):
    @staticmethod
    def create_session():
        engine = create_engine(db_scheme)
        Session = sessionmaker(bind = engine)
        session = Session()
        return session

class RedisPool(object):
    def __init__(self, rdb):
        self.rdb = rdb

    def get_pool(self):
        if self.rdb == "tcp":
            pool = TCPPORT_REDIS_POOL
            return pool
        elif self.rdb == "udp":
            pool = UDPPORT_REDIS_POOL
            return pool
        elif self.rdb == "offtcp":
            pool = OFFTCPPORT_REDIS_POOL
            return pool
        elif self.rdb == "offudp":
            pool = OFFUDPPORT_REDIS_POOL
            return pool
        else:
            return None
        
#session = create_session(engine)

#Session = sessionmaker(bind = init_engine)
#session = Session()

class DBdml(object):
    def __init__(self):
        #self.create_session = CreateSession()
        #self.sessions = self.create_session.create_session()
        #self.dbsession = self.sessions[str(os.getpid())]
        self.dbsession = CreateSession().create_session()
        #print "MySQL session is : %s" % (str(self.dbsession))
    def add_row(self, TableClass, *args, **kwargs):
        row = TableClass(*args, **kwargs)
        self.dbsession.add(row)
    def add_rows(self, TableClass, argslist):
        try:
            for args in argslist:
                row = apply(TableClass, args)
                self.dbsession.add(row)
            self.dbsession.commit()
        except Exception, e:
            self.dbsession.rollback()
            print e

    def del_rows(self, *tableobj):
        self.dbsession.delete(*tableobj)

    def commit(self):
        self.dbsession.commit()

    def rollback(self):
        self.dbsession.rollback()
    def close(self):
        self.dbsession.close()

class DBHandler(object):
    def __init__(self):
        self.dbm = DBdml()
    #def __del__(self):
    #    print "__del__: MySQL Session Distroy"
    #    self.dbm.close()
    #    del self.dbm
    
    def _add_it(self, TableClass, q_item, item):
        count_items = q_item.count()
        if count_items == 1:
            one_q_item = q_item.one()
            for i, v in item.items():
                setattr(one_q_item, i, v)
        elif count_items == 0:
            #dbm = DBdml()
            self.dbm.add_row(TableClass, **item)
        else:
            raise UniqException
        
    def add_portmonit(self, TableClass, ditemlist, queue):
        try:
            for item in ditemlist:
                q_item = self.dbm.dbsession.query(func.max(TableClass.updatetime)).filter_by(ip = item['ip'], port = item['port'], prot_type = item['prot_type'],reported = 1)
                if q_item.first()[0]:
                    q_item_first = q_item.first()
                    #print "qurue items True"
                    #print dir(q_item_first[0])
                    t_format = "%Y-%m-%d %H:%M:%S"
                    now = datetime.strftime(datetime.now(), t_format)
                    #diff_time = datetime.now() - strtotime(q_item['updatetime'], t_format).seconds
                    diff_time = (datetime.now() - q_item_first[0]).seconds
                    #print "diff_time: {0}".format(diff_time)
                    if diff_time > WARN_TIME:
                        item['reported'] = 1
                        self.dbm.add_row(TableClass, **item)
                        queue.put(1)
                    else:
                        queue.put(0)
                else:
                    #print "query items False"
                    item['reported'] = 1
                    self.dbm.add_row(TableClass, **item)
                    queue.put(1)
            self.dbm.commit()
        except Exception, e:
            self.dbm.rollback()
            print e
            print traceback.format_exc()
            queue.put(0)
                

    def add_portoff(self, TableClass, ditem):
        dictitem = ditem
        try:
            dictitem['reported'] = 1
            self.dbm.add_row(TableClass, **dictitem)
            self.dbm.commit()
        except Exception, e:
            self.dbm.rollback()
            print e
            print traceback.format_exc()
        finally:
            print "MySQL Session Distroy"
            #self.dbm.close()
            #del self.dbm

    
    def testhandle(self, TableClass):
        q_item = self.dbm.dbsession.query(TableClass).filter(TableClass.admin.like('y%'))
        print "test count: ", q_item.count()

   
       
class DBThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        self.job = func
        self.args = args
        self.kwargs = kwargs
        threading.Thread.__init__(self)
    def run(self):
        self.job(*self.args, **self.kwargs)

class MainBuffThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        self.job = func
        self.args = args
        self.kwargs = kwargs
        threading.Thread.__init__(self)
    def run(self):
        self.job(*self.args, **self.kwargs)

class SendMsgThread(threading.Thread):
    def __init__(self, func, *args, **kwargs):
        self.job = func
        self.args = args
        self.kwargs = kwargs
        threading.Thread.__init__(self)
    def run(self):
        if msglock.acquire():
            self.job(*self.args, **self.kwargs)
            msglock.release()
            
class RedisHandler(object):
    """
    def __init__(self, address, strports):
        self.address = address
        self.strports = strports
    """
    @staticmethod
    def init_storedb(address, strports):
        RedisHandler._instance = RedisHandler()
        RedisHandler._instance.address = address
        RedisHandler._instance.strports = strports
        return RedisHandler._instance
    @staticmethod
    def init_exist():
        RedisHandler._instance = RedisHandler()
        return RedisHandler._instance
        
    def setports(self, r, portlist):
            pipe = r.pipeline()
            for p in portlist:
                pipe.hset(self.address, p, 3)
            pipe.execute()

    def getports(self, r):
        dbportlist = r.hkeys(self.address)
        return dbportlist
    
    def getsendports(self, r, diffports):
        sendport = []
        for d in diffports:
            int_d = int(r.hget(self.address, d))
            if int_d == 0:
                sendport.append(d)
            else:
                int_d = int_d - 1
                r.hset(self.address, d, int_d)
        return sendport

    def diffport(self, dbports, ports):
        dbportset = set(dbports)
        portset = set(ports)
        difflist = dbportset - portset
        return list(difflist)
    
    def storedb(self, rdb):
        portlist = self.strports.split(":")
        p = RedisPool(rdb)
        redis_pool = p.get_pool()
        r = redis.Redis(connection_pool = redis_pool)
        self.setports(r, portlist)
        dbportlist = self.getports(r)
        diffports = self.diffport(dbportlist, portlist)
        if diffports:
            sendports = self.getsendports(r, diffports)
            #print "sendports: %s" %  (str(sendports))
            return sendports
        else:
            return []
    
    def check_monitport(self, address, porttype, port):
        abstime = time.time()
        dbkey = ":".join([address, str(port)])
        if porttype == "tcp":
            rdb = "offtcp"
        elif porttype == "udp":
            rdb = "offudp"
        else:
            return 0
        p = RedisPool(rdb)
        redis_pool = p.get_pool()
        r = redis.Redis(connection_pool = redis_pool)
        if r.exists(dbkey):
            #print "dbkey: %s exists in rdb" % (dbkey)
            return 0 
        else:
            try:
                r.setex(dbkey, abstime, WARN_TIME)
            except:
                return 0
            return 1
    
    def exists(self, *keys, **kwdb):
        exist_key = []
        dbs = kwdb.values()
        for db in dbs:
            p = RedisPool(db)
            redis_pool = p.get_pool()
            r = redis.Redis(connection_pool = redis_pool)
            for key in keys:
                if r.exists(key):
                    if key not in exist_key:
                        exist_key.append(key)
                    else:
                        pass
                else:
                    pass
        return exist_key
    
    def exists_one(self, key, **kwdb):
        exist = False
        dbs = kwdb.values()
        for db in dbs:
            p = RedisPool(db)
            redis_pool = p.get_pool()
            r = redis.Redis(connection_pool = redis_pool)
            if r.exists(key):
                exist = True
                return exist
            else:
                pass
        return exist
                
        
            
        
if __name__ == "__main__":
    print "__main__"
