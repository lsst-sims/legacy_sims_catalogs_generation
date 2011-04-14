#!/usr/bin/env python
from lsst.sims.catalogs.generation.db import jobDB
import sys

js = jobDB.JobState()
jobid = js.getJobId()
print jobid.getOwner(), jobid.getId()
js.updateState("mykey","my value")
print js.queryState("mykey")
js.updateState("mykey","now my value")
print js.queryState("mykey")
js.updateState("newkey", "my new key")
print js.queryState("newkey")
