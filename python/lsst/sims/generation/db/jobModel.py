from elixir import *
import sqlalchemy.databases as sd 
metadata.bind = "postgresql://jobreporter:jobreporter@deathray/joblog"
metadata.bind.echo = True

class JobLog (Entity):
  jobid = Field(Integer)
  pkey = Field(Unicode(15))
  pvalue = Field(UnicodeText)
  time = Field(DateTime(timezone=True))
  taskNumber = Field(Integer)
  ip = Field(sd.postgres.PGInet)
  description = Field(UnicodeText)
  def __repr__(self):
    return '<Log Event (%s,%s) at %s>' % (self.pkey, self.pvalue, self.time)

