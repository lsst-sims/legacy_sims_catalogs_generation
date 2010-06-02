#!/usr/bin/env python
from lsst.sims.catalogs.generation.db import jobDB
import sys
import time

js = jobDB.JobState()
jobid = js.getJobId()
print jobid
js.updateState("mykey","my value")
while True:
  print js.queryState("mykey")
  time.sleep(2)
