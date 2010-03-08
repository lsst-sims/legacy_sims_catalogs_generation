#!/usr/bin/env python
import jobDB as j
mj = j.jobDB()
mj.registerTaskStart()
for i in range(100):
  if(i%5 == 0):
    mj.registerEvent("event%i"%(i/5), eventdescription="Done %i of %i"%(i,100))
mj.persist("MyFakeMetric", (0.5, 1.0), "This is some sort of floating point value")
mj.registerTaskStop()
