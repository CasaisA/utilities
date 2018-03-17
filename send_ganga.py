j = Job(name='gen_ntuple2')
#myApp = prepareGaudiExec('Erasmus','v15r1',myPath = '/afs/cern.ch/user/a/acasaisv/cmtuser')
myApp = GaudiExec()

myApp.directory = "/afs/cern.ch/user/a/acasaisv/cmtuser/ErasmusDev_v15r1"

j.application = myApp
j.application.useGaudiRun = False
j.application.platform = 'x86_64-slc6-gcc62-opt'

j.application.options=['/afs/cern.ch/user/a/acasaisv/private/kspipiee/stripping/reco/ganga/gen_ganga.py']

j.application.readInputData('MC_2012_34124015_Beam4000GeV2012MagDownNu2.5Pythia8_Sim08e_Digi13_Trig0x409f0045_Reco14a_Stripping20NoPrescalingFlagged_ALLSTREAMS.DST.py')
#j.inputfiles=['/afs/cern.ch/user/a/acasaisv/private/mymod/diego/alyabar.py','/afs/cern.ch/user/a/acasaisv/private/mymod/diego/select.py','/afs/cern.ch/user/a/acasaisv/private/mymod/diego/probavector.py']
j.splitter = SplitByFiles ( filesPerJob = 1 , ignoremissing=True)
j.backend = Dirac()
j.outputfiles = [LocalFile('*.root')]
j.submit()
