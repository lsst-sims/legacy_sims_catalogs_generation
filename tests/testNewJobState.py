import lsst.sims.catalogs.generation.db.jobDB as jdb

#Make a couple of ids...
myid1 = jdb.JobId(10)
myid2 = jdb.JobId(10,"simon")

#make a couple of job states
js = {}
js["1"] = jdb.JobState(myid1)
js["2"] = jdb.JobState(myid2)
js["3"] = jdb.JobState()
js["4"] = jdb.JobState(11)

for k in js.keys():
  js[k].updateState("Updating with key", "Key is %s"%k)
  js[k].updateState("Updating with another key", "Key is %s"%k)

for k in js.keys():
  js[k].showStates()

js["1"].deleteStates()
js["2"].deleteStates()
js["3"].deleteStates()
js["4"].deleteStates()
