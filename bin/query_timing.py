import psycopg2 as pg
import numpy
import sys

def total_hours(td):
    return (td.microseconds+(td.seconds+td.days*4*3600)*10**6)/10**6/3600.

def count_running(r, results):
    n = 0
    for res in results:
        if r[1] >= res[1] and r[1] < res[2]:
            n += 1
    return n

conn = pg.connect(host="z.astro.washington.edu", database="joblog",
        user="jobreporter", password="jobreporter")
cur = conn.cursor()
qstr = """
select ftimes.jobid jobid, stimes.start_time start_time, ftimes.stop_time stop_time,
ftimes.stop_time-stimes.start_time runtime from
  (select jobid, max(time) start_time
     from eventlog
     where jobid in
     (select jobid
       from eventlog
       group by jobid
       order by max(time) desc)
     and pkey = 'TASK_START'
     group by jobid) stimes,
  (select jobid, max(time) stop_time
     from eventlog
     where jobid in
     (select jobid
        from eventlog
        group by jobid
        order by max(time) desc)
     and pkey = 'TASK_STOP'
     group by jobid) ftimes
  where stimes.jobid = ftimes.jobid order by start_time;
"""
cur.execute(qstr)
results = cur.fetchall()
res_o = results[0]
data = {'id':[], 'starttime':[], 'stoptime':[], 'runtime':[]}
for r in results:
    num = count_running(r, results)
    print r[0], r[1].isoformat(), r[2].isoformat(), total_hours(r[3]), num


