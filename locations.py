import os


repo = os.getenv("WORKDIR")
eoslhcb = os.getenv("EOSLHCB")
home = os.getenvt("HOME")
class loc:
    pass

loc.ROOT = repo
loc.PRIV = loc.ROOT+"/private"
loc.PLOTS = loc.PRIV+"/plots"
loc.TABS = loc.PRIV+"/tables"
locs.NTUP = loc.PRIV+"/ntuples"
loc.EOS = eoslhcb
loc.HOME = home
    
