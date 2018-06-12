
import aia_mkmovie as am

st_time = '2018/01/09 00:00:00'
en_time = '2018/01/10 23:59:00'

base=am.aia_mkmovie(st_time,en_time,193,cadence='3m',nproc=1,synoptic=False,download=True, email = 'miles.gordon@cfa.harvard.edu',prompt=False,rotation=False)
base.run_all()