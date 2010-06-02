#!/usr/bin/env python
from lsst.sims.catalogs.generation.db import jobDB
import sys

if len(sys.argv) < 2:
  print "Usage jobstate_update_test.py jobid"
  sys.exit(1)

jid = int(sys.argv[1])
js = jobDB.JobState(jobid=jid)
jobid = js.getJobId()
print jobid
print js.queryState("mykey")
print js.queryState("newkey")
js.updateState("mykey","value from second process")
print js.queryState("mykey")
js.updateState("newprocesskey", "brand new key/value from second process")
print js.queryState("newprocesskey")
