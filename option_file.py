import argparse
from Configurables import DaVinci



import GaudiPython
from PhysSelPython.Wrappers import DataOnDemand
from Configurables import CombineParticles, ChargedProtoParticleMaker, NoPIDsParticleMaker,DaVinci,ChargedPP2MC ,LoKi__VertexFitter

from CommonParticles import StdAllNoPIDsPions, StdAllNoPIDsElectrons, StdNoPIDsUpElectrons
from CommonParticles.Utils import *
from Gaudi.Configuration import NTupleSvc,GaudiSequencer

from KSPiPieeBENDER import MyAlg

#ARGUMENT PARSER
parser = argparse.ArgumentParser(description='Buids signal ntuple for KSPiPiee decay')
parser.add_argument('--polarity', choices = ['u','d'],
                                                            help='Polarity')
parser.add_argument('--input',help='In the case of not using ganga, the name of the DST inside the folder')

parser.add_argument("--fitter",help="Vertex fitter to be used",choices=["loki","particle","offline"])


args = parser.parse_args()



#MCTRUTH-MATCH

myprotos = ChargedProtoParticleMaker("MyProtoParticles",
                                     Inputs = ["Rec/Track/Best"],
                                     Output = "Rec/ProtoP/MyProtoParticles")

protop_locations = [myprotos.Output]
charged = ChargedPP2MC("myprotos")
charged.InputData = protop_locations
myseq = GaudiSequencer("myseq")
myseq.Members +=[myprotos,charged]
DaVinci().UserAlgorithms+=[myseq]
############                                                                                                                                                                                                       
                                                                                                                                                


## GET MCPAR FROM PROTO                                                                                                                                                                                            
def get_mcpar(proto):
    LinkRef = GaudiPython.gbl.LHCb.LinkReference()
    linker = TES["Link/Rec/ProtoP/MyProtoParticles/PP2MC"]
    ok = linker.firstReference(proto.key(), None ,LinkRef)
    if not ok: return 0
    return TES["MC/Particles"][LinkRef.objectKey()]


#VELO PARTICLES MAKER                                                                                                                                                                                       
algorithm =  NoPIDsParticleMaker ( 'StdNoPIDsVeloElectrons',
                                   DecayDescriptor = 'Electron' ,
                                   Particle = 'electron',
                                   AddBremPhotonTo= [],
                                   Input = myprotos.Output)

# TRACK SELECTOR CONFIG                                                                                                                                                                                     
selector = trackSelector ( algorithm,trackTypes = [ "Velo" ]  )
locations = updateDoD ( algorithm )
########################                                                                                                                                                                                           

## build all possible combinations of track types                                                                                                                                                                  
combs = {"LL":"( ANUM( ( TRTYPE == 3 ) &  ( ABSID == 'e-' ) ) == 2 )",
         "UU":"( ANUM( ( TRTYPE == 4 ) &  ( ABSID == 'e-' ) ) == 2 )",
         "VV":"( ANUM( ( TRTYPE == 1 ) &  ( ABSID == 'e-' ) ) == 2 )",
         "LU":"( ( ANUM( ( TRTYPE == 3 ) &  ( ABSID == 'e-' ) ) == 1 ) & ( ANUM( ( TRTYPE == 4 ) & ( ABSID == 'e-' ) ) == 1 ) )",
         "LV":"( ( ANUM( ( TRTYPE == 3 ) &  ( ABSID == 'e-' ) ) == 1 ) & ( ANUM( ( TRTYPE == 1 ) & ( ABSID == 'e-' ) ) == 1 ) )",
         "UV":"( ( ANUM( ( TRTYPE == 4 ) &  ( ABSID == 'e-' ) ) == 1 ) & ( ANUM( ( TRTYPE == 1 ) & ( ABSID == 'e-' ) ) == 1 ) )"}



#Offline and Particle not working yet DO NOT USE
#from Configurables import OfflineVertexFitter, ParticleVertexFitter


for name in combs:
    Ks2pipiee[name] = CombineParticles("TrackSel"+name+"_Ks2pipiee")

    if "V" in name:
        Ks2pipiee[name].DecayDescriptors = ["KS0 -> pi+ pi- e+ e-","KS0 -> pi+ pi- e+ e+","KS0 -> pi+ pi- e- e-"]
        if args.fitter=='loki':
           Ks2pipiee[name].ParticleCombiners = {"" : "LoKi::VertexFitter"}
           Ks2pipiee[name].addTool( LoKi__VertexFitter, name="LoKi::VertexFitter" )
        if args.fitter=='particle':

           Ks2pipiee[name].ParticleCombiners = {"" : "ParticleVertexFitter"}
           Ks2pipiee[name].addTool( ParticleVertexFitter)
        if args.fitter=='offline':
           Ks2pipiee[name].ParticleCombiners = {"" : "OfflineVertexFitter"}
           Ks2pipiee[name].addTool( OfflineVertexFitter)

    else: Ks2pipiee[name].DecayDescriptor = "KS0 -> pi+ pi- e+ e-"
    Ks2pipiee[name].Preambulo=["from LoKiPhysMC.decorators import *",
                               "from LoKiPhysMC.functions import mcMatch"]
    ## only take pions mctruth matched to pions from signal...                                                                                                                                                     
    Ks2pipiee[name].DaughtersCuts = {"pi+"  : "mcMatch('KS0 ==>  ^pi+ pi- e+ e-' )",
                                     "pi-"  : "mcMatch('KS0 ==>  pi+ ^pi- e+ e-' )"}
    Ks2pipiee[name].CombinationCut = combs[name]
    Ks2pipiee[name].MotherCut = "ALL"
    ## input all possible daughters                                                                                                                                                                                
    Ks2pipiee[name].Inputs =['Phys/StdAllNoPIDsPions', 'Phys/StdAllNoPIDsElectrons', 'Phys/StdNoPIDsUpElectrons', 'Phys/StdNoPIDsVeloElectrons']
    DaVinci().UserAlgorithms +=[Ks2pipiee[name]]


def is_el_from_ks(proto):
    if not proto: return False
    mcpar = get_mcpar(proto)
    if not mcpar: return False
    if abs(mcpar.particleID().pid()) != 11: return False
    mum = mcpar.mother()
    if not mum: return False
    if mum.particleID().pid()!=310: return False
    pids = map(lambda x: abs(x.particleID().pid()),mum.endVertices()[-1].products())
    if pids.count(11)!=2: return False
    if pids.count(211)!=2: return False
    return mcpar.key(),mum.key()

#DAVINCI OPTIONS
DaVinci().EvtMax = 0
DaVinci().DataType = "2012"
DaVinci().Simulation = True
DaVinci().DDDBtag  = "dddb-20130929-1"
DaVinci().CondDBtag = "sim-20130522-1-vc-m"+args.polarity+"100"

                                                                                                                             
                                                                                                        
#INPUTS
if str(sys.argv[1])=="u":
     DaVinci().Input = ["/eos/lhcb/grid/prod/lhcb/MC/2012/ALLSTREAMS.DST/00037694/0000/"+args.input]

if str(sys.argv[1])=="d":
     DaVinci().Input = ["/eos/lhcb/grid/prod/lhcb/MC/2012/ALLSTREAMS.DST/00037700/0000/"+args.input]

#OUTPUTS


if args.polarity=="u":
    if args.fitter=='offline':
      DaVinci().TupleFile = dir+"/OfflineVertexFit/up/"+args.input+".root"
    if args.fitter=='particle':
      DaVinci().TupleFile = dir+"/ParticleVertexFit/up/"+args.input+".root"
    if args.fitter=='loki':
      DaVinci().TupleFile = dir+"/LokiVertexFit/up/"+args.input+".root"
if args.polarity=="d":
    if args.fitter=='offline':
       DaVinci().TupleFile = dir+"/OfflineVertexFit/down/"+args.input+".root"
    if args.fitter=='particle':
       DaVinci().TupleFile = dir+"/ParticleVertexFit/down/"+args.input+".root"
    if args.fitter=='loki':
       DaVinci().TupleFile = dir+"/LokiVertexFit/down/"+args.input+".root"


#NTUPLE PRODUCTION BENDER CLASS


#RUNNING
                
gaudi = GaudiPython.AppMgr()


for name in combs:
    gaudi.addAlgorithm(MyAlg(name))




gaudi.initialize()
gaudi.run(-1)
gaudi.stop()
gaudi.finalize()             
