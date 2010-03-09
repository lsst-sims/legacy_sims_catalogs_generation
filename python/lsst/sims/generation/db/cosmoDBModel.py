#!/usr/bin/env python
from elixir import *
from sqlalchemy import func
from sqlalchemy import schema
metadata.bind = "postgresql://cosmouser:cosmouser@deathray/cosmoDB.11.19.2009"
metadata.bind.echo = False
class Star(Entity):
  using_options(tablename="stars", autoload=True)

class OpSim3_61(Entity):
  using_options(tablename="output_opsim3_61", autoload=True)
