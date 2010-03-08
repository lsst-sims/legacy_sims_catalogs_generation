from elixir import *
from sqlalchemy.databases.postgres import PGInet
metadata.bind = "postgres://jobreporter:jobreporter@deathray/joblog"
metadata.bind.echo = True

class JobLog (Entity):
  jobid = Field(Integer)
  pkey = Field(Unicode(15))
  pvalue = Field(UnicodeText)
  time = Field(DateTime(timezone=True))
  taskNumber = Field(Integer)
  ip = Field(PGInet)
  description = Field(UnicodeText)
  def __repr__(self):
    return '<Log Event (%s,%s) at %s>' % (self.pkey, self.pvalue, self.time)

