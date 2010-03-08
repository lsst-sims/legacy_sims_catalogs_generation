#!/usr/bin/env python
from jobModel import *
from sqlalchemy import func
import datetime as dt
import socket

class jobDB(object):
  def __init__(self, jobid=None, jobdescription="", ip = None):
    setup_all()
    self._tasknumber = None
    if jobid is None:
      self._jobid = session.query(func.max(JobLog.jobid)).one()[0] + 1
    else:
      self._jobid = jobid
    self._jobdescription = jobdescription
    if ip is None:
      self._ip = socket.gethostbyname(socket.gethostname())
    else:
      self._ip = ip

  def persist(self, key, value, description):
    print "Persisting Task number %s"%(str(self._tasknumber))
    JobLog(jobid=self._jobid, pkey=key, pvalue=value, time=dt.datetime(1,1,1).now(), taskNumber=self._tasknumber, ip=self._ip, description=description)
    session.commit()

  def registerTaskStart(self, tasknumber=None):
    key = "TASK_START" 
    if tasknumber is None:
      tasknumber = session.query(func.max(JobLog.taskNumber)).one()[0]
      print "Task number %s"%(str(tasknumber))
      if tasknumber is None:
        tasknumber = 1
    else:
      pass
    self._tasknumber = tasknumber
    print "Task number %s"%(str(self._tasknumber))
    value = "Task started"
    self.persist(key, value, self._jobdescription)
    
  def registerEvent(self, eventid, eventdescription=""):
    key = "TASK_EVENT"
    value = eventid
    self.persist(key, value, eventdescription)

  def registerTaskStop(self, exitvalue=1):
    key = "TASK_STOP"
    value = "Task number %s stopped with term value %s"%(str(self._tasknumber), str(exitvalue))
    self.persist(key, value, self._jobdescription)

  
