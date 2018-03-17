from Configurables import (
    DaVinci,
    EventSelector,
    PrintMCTree,
    MCDecayTreeTuple
    )

from DecayTreeTuple.Configuration import *
year = 2012
decay = "[KS0 ==> ^pi+ ^pi- ^e+ ^e-]CC"

import sys
# HOME = "/afs/cern.ch/work/j/jcidvida/tmp/xgen_emu/"
# #if len(sys.argv)==1: datafile = HOME+"proba_40112030_mA_2_tA_0.gen"
# if len(sys.argv)==1: datafile = "/tmp/jcidvida/proba.gen"
# else: datafile = HOME+filter(lambda x: sys.argv[1] in x,os.listdir(HOME))[0]


# For a quick and dirty check, you don't need to edit anything below here.
##########################################################################

# Create an MC DTT containing any candidates matching the decay descriptor
mctuple = MCDecayTreeTuple("MCDecayTreeTuple")
mctuple.Decay = decay
mctuple.addBranches({"KSO":"[KS0 ==> pi+ pi-  e+ e-]CC",
                     "e+":"[KS0 ==> pi+ pi-  ^e+ e-]CC",
                     "e-":"[KS0 ==> pi+ pi-  e+ ^e-]CC",
                     "pi+":"[KS0 ==> ^pi+ pi-  e+ e-]CC",
                     "pi-":"[KS0 ==> pi+ ^pi-  e+ e-]CC"})

mctuple.ToolList = [
    "MCTupleToolHierarchy",
    "LoKi::Hybrid::MCTupleTool/LoKi_Photos"
    ]
# Add a 'number of photons' branch
mctuple.addTupleTool("MCTupleToolKinematic").Verbose = True
mctuple.addTupleTool("LoKi::Hybrid::TupleTool/LoKi_Photos").Variables = {
    "nPhotos": "MCNINTREE(('gamma' == MCABSID))"
    }

mctuple.addTupleTool("LoKi::Hybrid::MCTupleTool/LoKi_All")
mctuple.LoKi_All.Variables =  {
    'TRUEID' : 'MCID',
    'M'      : 'MCMASS',
    'THETA'  : 'MCTHETA',
    'PT'     : 'MCPT',
    'PX'     : 'MCPX',
    'PY'     : 'MCPY',
    'PZ'     : 'MCPZ',
    'ETA'    : 'MCETA',
    'PHI'    : 'MCPHI'
    }

# Name of the .xgen file produced by Gauss
#EventSelector().Input = ["DATAFILE='{0}' TYP='POOL_ROOTTREE' Opt='READ'".format(datafile)]

# Configure DaVinci
DaVinci().Simulation = True
DaVinci().UserAlgorithms = [mctuple]
DaVinci().EvtMax = 0
DaVinci().DataType = "2012"
DaVinci().Simulation = True
DaVinci().DDDBtag  = "dddb-20130929-1"
DaVinci().CondDBtag = "sim-20130522-1-vc-m"+str(sys.argv[1])+"100"

if sys.argv[1]=="u":
    DaVinci().Input = ["/eos/lhcb/grid/prod/lhcb/MC/2012/ALLSTREAMS.DST/00037694/0000/"+str(sys.argv[2])]
if sys.argv[1]=="d":
    DaVinci().Input = ["/eos/lhcb/grid/prod/lhcb/MC/2012/ALLSTREAMS.DST/00037700/0000/"+str(sys.argv\
                                                                                            [2])]
DaVinci().TupleFile = "/eos/lhcb/user/a/acasaisv/kspipiee/stripping/mctruth/"+sys.argv[2]+".root"




import GaudiPython
gaudi = GaudiPython.AppMgr()
gaudi.initialize()
TES = gaudi.evtsvc()
gaudi.run(-1)
gaudi.stop()
gaudi.finalize()
