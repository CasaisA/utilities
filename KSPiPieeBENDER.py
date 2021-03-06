#! /usr/bin/env python
# -*- coding: utf-8 -*-
import GaudiPython
# from PhysSelPython.Wrappers import DataOnDemand
# from Configurables import CombineParticles, ChargedProtoParticleMaker, NoPIDsParticleMaker,DaVinci,ChargedPP2MC ,LoKi__VertexFitter

# from CommonParticles import StdAllNoPIDsPions, StdAllNoPIDsElectrons, StdNoPIDsUpElectrons
# from CommonParticles.Utils import *
# from Gaudi.Configuration import NTupleSvc,GaudiSequencer
from Bender.MainMC import *
from SomeUtils.alyabar import *   
from LinkerInstances.eventassoc import * 
from ROOT import *
import math as m
from BenderAlgo.select import selectVertexMin
from copy import copy





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

    


#class to produce the nTuple
c_light = 299.792458
light_cte = 1000./c_light
emass = 0.510998
pimass = 139.5706

gaudi = GaudiPython.AppMgr()
TES = gaudi.evtsvc()

##class to make the ntuple

class MyAlg(AlgoMC):
    def analyse(self):
        #YOU NEED TO HAVE DEFINED THE PROPER TES DIRECTORY IN ORDER TO MAKE THIS WORK!
        ks0s = TES["Phys/TrackSel"+str(self.name())+"_Ks2pipiee/Particles"]
        mytup1 = self.nTuple(self.name())
        CandidateInfo = {}
        #this is for the vertex
        pvs_ = self.vselect("pvs_", ISPRIMARY)
        if not pvs_.size(): return SUCCESS
        ips2cuter = MIPCHI2(pvs_,self.geo())
        for ks in ks0s:
             
             if not ks: continue
             if not ks.daughters():continue
             daughters = map(lambda x: is_el_from_ks(x.proto()),ks.daughters())
             daughters = filter(lambda y: type(y)!=bool,daughters)
             if len(daughters)!=2: continue
             if daughters[0][0]==daughters[1][0]: continue
             if daughters[0][1]!=daughters[1][1]: continue
             ## 1:plus 2:minus
             pi1  = ks.daughters()[0]
             pi2 = ks.daughters()[1]
             e1   = ks.daughters()[2]
             e2  = ks.daughters()[3]
             #SELECTING THE VERTEX
             PVips2 = VIPCHI2( ks, self.geo())
             PV = selectVertexMin(pvs_, PVips2, (PVips2 >= 0. ))
             if not PV:
                 continue
             
             
             ctau = CTAU(PV)
             KSlife_ = ctau(ks)#mm
             KSlife_ps = KSlife_*light_cte #picoseconds
             Dis2 = VDCHI2(PV)
             PVvec = vector( VX(PV), VY(PV), VZ(PV) )
             SVvec = vector( VX(ks.endVertex()), VY(ks.endVertex()), VZ(ks.endVertex()) )
             rSV = SVvec - PVvec

             KSp = vector(PX(ks), PY(ks), PZ(ks))
       
             KSpt = vtmod(KSp)
             KSips2 = PVips2(PV)
             KSip = dpr(PVvec, SVvec, KSp)



             pi1ips2, pi2ips2,e1ips2,e2ips2 = ips2cuter(pi1), ips2cuter(pi2),ips2cuter(e1),ips2cuter(e2)
             sigDOFS = Dis2(ks)

             ipscheck = min(sigDOFS, pi1ips2, pi2ips2,e1ips2, e2ips2, KSips2)
             
             if sigDOFS<0: continue
             sigDOFS = m.sqrt(sigDOFS)
             if KSips2<0: continue 
             KSips = m.sqrt(KSips2)

             trackpi1 = pi1.proto().track()
             trackpi2 = pi2.proto().track()
             tracke1  = e1.proto().track()
             tracke2  = e2.proto().track()
             opi1, opi2,oe1,oe2 = trackpi1.position(), trackpi2.position(), tracke1.position(), tracke2.position()
             mippvs = MIP( pvs_, self.geo() )
             iptoPV = IP (PV, self.geo())
             mipchi2pvs_ = MIPCHI2(pvs_, self.geo())
             ipchi2PV = IPCHI2(PV, self.geo())
            
             e1ippvs_ = mippvs (e1) # IP
             e2ippvs_ = mippvs (e2)
             pi1ippvs_ = mippvs (pi1)
             pi2ippvs_ = mippvs (pi2)
             
             pi1ip_ = iptoPV (pi1)
             pi2ip_ = iptoPV (pi2)
             e1ip_ = iptoPV (e1)
             e2ip_ = iptoPV (e2)        #

             
             
             
             CandidateInfo["ipscheck"]=ipscheck
             CandidateInfo["SVChi2"]= VCHI2(ks.endVertex())

             
             CandidateInfo["pi1mip"] = pi1ippvs_
             CandidateInfo["pi2mip"] = pi2ippvs_
             CandidateInfo["e1mip"] = e1ippvs_
             CandidateInfo["e2mip"] = e2ippvs_
             CandidateInfo["pi1ip"]=pi1ip_
             CandidateInfo["pi2ip"]=pi2ip_
             CandidateInfo["e1ip"]=e1ip_
             CandidateInfo["e2ip"]=e2ip_
             CandidateInfo["pi1mipchi2"] = mipchi2pvs_(pi1)
             CandidateInfo["pi2mipchi2"] = mipchi2pvs_(pi2)
             CandidateInfo["e1mipchi2"] = mipchi2pvs_(e1)
             CandidateInfo["e2mipchi2"] = mipchi2pvs_(e2)

             CandidateInfo["pi1ipchi2"] = ipchi2PV(pi1)
             CandidateInfo["pi2ipchi2"] = ipchi2PV(pi2)
             CandidateInfo["e1ipchi2"] = ipchi2PV(e1)
             CandidateInfo["e2ipchi2"] = ipchi2PV(e2)
             
             CandidateInfo["Ksctau"] = KSlife_ ## in milimeters !!!!!
             CandidateInfo["KSlife_ps"] = KSlife_ps  ### in ps !!
             CandidateInfo["Ksmass"] = M(ks)
             CandidateInfo["ks_p1"]=PX(ks)
             CandidateInfo["ks_p2"]=PY(ks)
             CandidateInfo["ks_p3"]=PZ(ks)
             CandidateInfo["ks_p"]=P(ks)
             CandidateInfo["ks_pt"]=PT(ks)
             #########################
             ##i calculate the 6 combinantions for DOCA
             ## e1pi1 e1pi2 e1e2 e2pi1 e2pi2 pi1pi2
             DOCA_func = []
             DOCA_func.append(CLAPP(e1,self.geo()))
             DOCA_func.append(CLAPP(e2,self.geo()))
             DOCA_func.append(CLAPP(pi1,self.geo()))
             DOCA = {}
             DOCA["e1pi1"]=DOCA_func[0](pi1)
             DOCA["e1pi2"]=DOCA_func[0](pi2)
             DOCA["e1e2"]=DOCA_func[0](e2)
             DOCA["e2pi1"]=DOCA_func[1](pi1)
             DOCA["e2pi2"]=DOCA_func[1](pi2)
             DOCA["pi1pi2"]=DOCA_func[2](pi2)

             DOCAMIN_key = min(DOCA,key=DOCA.get)
             DOCAMIN_ = DOCA[DOCAMIN_key]
             ###################
             CandidateInfo["DOCAMIN"]=DOCAMIN_
             if DOCAMIN_key == "e1pi1":   CandidateInfo ["DOCAMIN_comb"]=1
             elif DOCAMIN_key == "e1pi2": CandidateInfo ["DOCAMIN_comb"]=2
             elif DOCAMIN_key == "e1e2": CandidateInfo  ["DOCAMIN_comb"]=3
             elif DOCAMIN_key == "e2pi1": CandidateInfo ["DOCAMIN_comb"]=4
             elif DOCAMIN_key == "e2pi2": CandidateInfo ["DOCAMIN_comb"]=5
             elif DOCAMIN_key == "pi1pi2": CandidateInfo["DOCAMIN_comb"]=6
             else: CandidateInfo["DOCAMIN_comb"]=7

             DOCAMAX_key = max(DOCA,key=DOCA.get)
             DOCAMAX_ = DOCA[DOCAMAX_key]
             ###################
             CandidateInfo["DOCAMAX"]=DOCAMAX_
             if DOCAMAX_key == "e1pi1":   CandidateInfo ["DOCAMAX_comb"]=1
             elif DOCAMAX_key == "e1pi2": CandidateInfo ["DOCAMAX_comb"]=2
             elif DOCAMAX_key == "e1e2": CandidateInfo  ["DOCAMAX_comb"]=3
             elif DOCAMAX_key == "e2pi1": CandidateInfo ["DOCAMAX_comb"]=4
             elif DOCAMAX_key == "e2pi2": CandidateInfo ["DOCAMAX_comb"]=5
             elif DOCAMAX_key == "pi1pi2": CandidateInfo["DOCAMAX_comb"]=6
             else: CandidateInfo["DOCAMAX_comb"]=7

             
        
             #KINEMATIC

             CandidateInfo["e1p1"] = PX(e1)
             CandidateInfo["e1p2"] = PY(e1)
             CandidateInfo["e1p3"] = PZ(e1)
             CandidateInfo["e2p1"] = PX(e2)
             CandidateInfo["e2p2"] = PY(e2)
             CandidateInfo["e2p3"] = PZ(e2)

             CandidateInfo["pi1p1"]= PX(pi1)
             CandidateInfo["pi1p2"]= PY(pi1)
             CandidateInfo["pi1p3"]= PZ(pi1)
             CandidateInfo["pi2p1"]= PX(pi2)
             CandidateInfo["pi2p2"]= PY(pi2)
             CandidateInfo["pi2p3"]= PZ(pi2)

             CandidateInfo["e1pt"]  = PT(e1)
             CandidateInfo["e1ptot"] = P(e1)
             CandidateInfo["e2pt"]  = PT(e2)
             CandidateInfo["e2ptot"] = P(e2)

             CandidateInfo["pi1pt"]  = PT(pi1)
             CandidateInfo["pi1ptot"] = P(pi1)
             CandidateInfo["pi2pt"]  = PT(pi2)
             CandidateInfo["pi2ptot"] = P(pi2)

             mfit_dtf1  = DTF_FUN  ( M , True , strings('e+','e-') )
             mfit_dtf2 = DTF_FUN  ( M , True)

             CandidateInfo["KS_mfit_dtf1"]=mfit_dtf1(ks)
             CandidateInfo["KS_mfit_dtf2"]=mfit_dtf2(ks)
             
             ##Invariant masses

             #for the categories LL,LU,LV,UU AND UV
             #We will consdier always a 'good' which will give us the kinematic info
             #and a 'bad' track that only will give us the kinematic constraint

             #for LU,LV the good will always be the LONG track

             #for UV it will be the upstream

             #for UU and LL it will be the one with less error in the momentum

             #######################################################################

             #Initialization of the kinematic variables
             ux = VX(ks.endVertex())-VX(PV)
             uy = VY(ks.endVertex())-VY(PV)
             uz = VZ(ks.endVertex())-VZ(PV)
             e1_mc = get_mcpar(e1.proto())
             # e2_mc = get_mcpar(e2.proto())
             # pi1_mc = get_mcpar(pi1.proto())
             # pi2_mc = get_mcpar(pi1.proto())
             #dont need every mcpar for now
             
             #TRUTH-V for for comparison with the fit
             ux_t = e1_mc.mother().originVertex().position().x()-e1_mc.mother().endVertices()[-1].position().x()
             uy_t = e1_mc.mother().originVertex().position().y()-e1_mc.mother().endVertices()[-1].position().y()
             uz_t = e1_mc.mother().originVertex().position().z()-e1_mc.mother().endVertices()[-1].position().z()
             
             u = TVector3(ux,uy,uz)
             u_t = TVector3(ux_t,uy_t,uz_t)
             u.SetMag(1.)
             #uprim e uprima, o vector resultante dos outros tres,
             #que ten q ser coplanario co momento do electron/positron
             p_piplus = TVector3(PX(pi1),PY(pi1),PZ(pi1))
             p_piminus = TVector3(PX(pi2),PY(pi2),PZ(pi2))
             p_eplus = TVector3(PX(e1),PY(e1),PZ(e1))
             p_eminus = TVector3(PX(e2),PY(e2),PZ(e2))
             #Now I will define the four vector of the dielectron
             #to get the non constrained mass which is the one
             #that I can use to cut in the Stripping
             Peplus= TLorentzVector(); Peplus.SetVectM(p_eplus,emass)
             Peminus = TLorentzVector();Peminus.SetVectM(p_eminus,emass)
             Pdielectron_r = Peplus + Peminus
             CandidateInfo['eeMass']=Pdielectron_r.M()
             uprim = p_piplus + p_piminus
             VVevent = False
             #specification of the 'good' and 'bad' electron momentums
             if (e1.proto().track().type()==1 and e2.proto().track().type()==3) or (e1.proto().track().type()==3 and e2.proto().track().type()==1) : #LV   
        	if e1.proto().track().type() == 1:
                    pgood = p_eminus
                    pbad = p_eplus
                else:
                    pgood = p_eplus
                    pbad = p_eminus

             elif (e1.proto().track().type()==4 and e2.proto().track().type()==3) or (e1.proto().track().type()==3 and e2.proto().track().type()==4) : #LU   
        	if e1.proto().track().type() == 4:
                    pgood = p_eminus
                    pbad = p_eplus
                else:
                    pgood = p_eplus
                    pbad = p_eminus
             elif (e1.proto().track().type()==4 and e2.proto().track().type()==1) or (e1.proto().track().type()==1 and e2.proto().track().type()==4) : #UV
                if e1.proto().track().type() == 1:
                    pgood = p_eminus
                    pbad = p_eplus
                else:
                    pgood = p_eplus
                    pbad = p_eminus
             elif (e1.proto().track().type()==3 and e2.proto().track().type()==3):#LL                                 
                 if e1.p().error()>=e2.p().error():
                    pgood = p_eminus
                    pbad = p_eplus
                 else:
                    pgood = p_eplus
                    pbad = p_eminus
             elif (e1.proto().track().type()==4 and e2.proto().track().type()==4):#UU
                 if e1.p().error()>=e2.p().error():
                    pgood = p_eminus
                    pbad = p_eplus
                 else:
                    pgood = p_eplus
                    pbad = p_eminus
        
             elif (e1.proto().track().type()==1 and e2.proto().track().type()==1): #LL
                VVevent = True
                #this names are simplier, actually are both equally bad :)
                pgood = p_eplus
                pbad  = p_eminus
                 
                 
             else:
                continue
             pbad_t = copy(pbad)
             pgood_t = copy(pgood)
             if not VVevent:
                
                uprim = uprim +pgood
                sinthetapbad = m.sin(u.Angle(pbad))
                sinthetauprim = m.sin(u.Angle(uprim))

                pe=sinthetauprim/sinthetapbad*uprim.Mag()
                pbad.SetMag(pe)
                
                P_piplus = TLorentzVector(); P_piplus.SetVectM(p_piplus,pimass)
                P_piminus = TLorentzVector();P_piminus.SetVectM(p_piminus,pimass)
                Pgood = TLorentzVector(); Pgood.SetVectM(pgood,emass)
                Pbad = TLorentzVector();Pbad.SetVectM(pbad,emass) 

            
                Ptot = P_piplus + P_piminus + Pgood + Pbad

                Pdielectron = Pgood + Pbad
                CandidateInfo['eeMassCo']=Pdielectron.M()
                CandidateInfo['KSMassCo']=Ptot.M()
                ######################################### trueV
                
                sinthetapbad_t = m.sin(u_t.Angle(pbad_t))
                sinthetauprim_t = m.sin(u_t.Angle(uprim))

                pe_t=sinthetauprim_t/sinthetapbad_t*uprim.Mag()
                pbad_t.SetMag(pe_t)
                
                
                
                Pbad_t = TLorentzVector();Pbad_t.SetVectM(pbad_t,emass) 

            
                Ptot_t = P_piplus + P_piminus + Pgood + Pbad_t

                Pdielectron_t = Pgood + Pbad_t
                CandidateInfo['eeMassCoTrueV']=Pdielectron_t.M()
                CandidateInfo['KSMassCoTrueV']=Ptot_t.M()
             else:
                pgood.SetMag(1.)
                pbad.SetMag(1.)
                pe = pgood + pbad
                #resultant angle of the two pions/electrons with respect to the incident ks0
                sinthetauprim = m.sin(u.Angle(uprim))
                sinthetae = m.sin(u.Angle(pe))
                pe.SetMag(uprim.Mag()*sinthetauprim/sinthetae)
                costhetapgood = m.cos(pgood.Angle(pe))
                costhetapbad = m.cos(pbad.Angle(pe))
                pgood.SetMag(pe.Mag()/(costhetapbad+costhetapgood))
                pbad.SetMag(pgood.Mag())
                
                P_piplus = TLorentzVector(); P_piplus.SetVectM(p_piplus,pimass)
                P_piminus = TLorentzVector();P_piminus.SetVectM(p_piminus,pimass)
                Pgood = TLorentzVector(); Pgood.SetVectM(pgood,emass)
                Pbad = TLorentzVector();Pbad.SetVectM(pbad,emass) 

            
                Ptot = P_piplus + P_piminus + Pgood + Pbad
                Pdielectron = Pgood + Pbad

                CandidateInfo['eeMass']=Pdielectron.M()
                CandidateInfo['KSMassCo']=Ptot.M()

                ########################################### trueV

                pgood_t.SetMag(1.)
                pbad_t.SetMag(1.)
                pe_t = pgood_t + pbad_t
                #resultant angle of the two pions/electrons with respect to the incident ks0
                sinthetauprim_t = m.sin(u_t.Angle(uprim))
                sinthetae_t = m.sin(u_t.Angle(pe_t))
                pe_t.SetMag(uprim.Mag()*sinthetauprim_t/sinthetae_t)
                costhetapgood_t = m.cos(pgood_t.Angle(pe_t))
                costhetapbad_t = m.cos(pbad_t.Angle(pe_t))
                pgood_t.SetMag(pe_t.Mag()/(costhetapbad_t+costhetapgood_t))
                pbad_t.SetMag(pgood_t.Mag())
                
                
                Pgood_t = TLorentzVector(); Pgood_t.SetVectM(pgood_t,emass)
                Pbad_t = TLorentzVector();Pbad_t.SetVectM(pbad_t,emass) 

            
                Ptot_t = P_piplus + P_piminus + Pgood_t + Pbad_t

                Pdielectron_t = Pgood_t+Pbad_t

                CandidateInfo['eeMassTruePV']=Pdielectron_t.M()
                CandidateInfo['KSMassCoTrueV']=Ptot.M()
                
            
        
             #TRACK TYPE
             
             CandidateInfo["e1TrackType"]=TRTYPE(e1)
             CandidateInfo["e2TrackType"]=TRTYPE(e2)
             CandidateInfo["pi1TrackType"]=TRTYPE(pi1)
             CandidateInfo["pi2TrackType"]=TRTYPE(pi2)
             

             
             #PID

             CandidateInfo["e1PIDe"]=PIDe(e1)
             CandidateInfo["e2PIDe"]=PIDe(e2)

             CandidateInfo["pi1PIDK"]=PIDK(pi1)
             CandidateInfo["pi2PIDK"]=PIDK(pi2)

             CandidateInfo["e1PIDtrue"]=get_mcpar(e1.proto()).particleID().pid()
             CandidateInfo["e2PIDtrue"]=get_mcpar(e2.proto()).particleID().pid()

             
             #WRONG CHARGE
             CandidateInfo["e1Charge"]=e1.charge()
             CandidateInfo["e2Charge"]=e2.charge()
             
             #MASSES FROM VECTORS (MAYBE BAD FIT)
             CandidateInfo["KSMMass"]=MM(ks)
             mothermom = e1.momentum()+e2.momentum()+pi1.momentum()+pi2.momentum()
             CandidateInfo["KSMMassbyHand"]= mothermom.M()




             #TRACKS AND VERTEX

             CandidateInfo["e1o1"] = e1.proto().track().position().x()
             CandidateInfo["e1o2"] = e1.proto().track().position().y()
             CandidateInfo["e1o3"] = e1.proto().track().position().z()
             CandidateInfo["e2o1"] = e2.proto().track().position().x()
             CandidateInfo["e2o2"] = e2.proto().track().position().y()
             CandidateInfo["e2o3"] = e2.proto().track().position().z()

             CandidateInfo["pi1o1"] = pi1.proto().track().position().x()
             CandidateInfo["pi1o2"] = pi1.proto().track().position().y()
             CandidateInfo["pi1o3"] = pi1.proto().track().position().z()
             CandidateInfo["pi2o1"] = pi2.proto().track().position().x()
             CandidateInfo["pi2o2"] = pi2.proto().track().position().y()
             CandidateInfo["pi2o3"] = pi2.proto().track().position().z()

             CandidateInfo["SV1"] = VX(ks.endVertex())           
             CandidateInfo["SV2"] = VY(ks.endVertex())           
             CandidateInfo["SV3"] = VZ(ks.endVertex())          
             CandidateInfo["evtNum"] = TES["Rec/Header"].evtNumber()
             CandidateInfo["runNum"] = TES["Rec/Header"].runNumber()

             CandidateInfo["PV1"] = VX(PV)
             CandidateInfo["PV2"] = VY(PV)
             CandidateInfo["PV3"] = VZ(PV)
             CandidateInfo["PVChi2"]=VCHI2(PV)
             CandidateInfo["KSipchi2"] = KSips2
             CandidateInfo["KS_ip" ] =  KSip
             CandidateInfo["KSdissig"]= sigDOFS
             


             CandidateInfo["e1_track_Chi2"] = TRCHI2 (e1)
             CandidateInfo["e2_track_Chi2"] = TRCHI2 (e2)

             CandidateInfo["e1_track_Chi2dof"] = TRCHI2DOF (e1)
             CandidateInfo["e2_track_Chi2dof"] = TRCHI2DOF (e2)

             CandidateInfo["pi1_track_Chi2"] = TRCHI2 (pi1)
             CandidateInfo["pi2_track_Chi2"] = TRCHI2 (pi2)

             CandidateInfo["pi1_track_Chi2dof"] = TRCHI2DOF (pi1)
             CandidateInfo["pi2_track_Chi2dof"] = TRCHI2DOF (pi2)

             theDira = DIRA(PV)
             CandidateInfo["DIRA"]=theDira(ks)
             #PROB
             CandidateInfo["e1PROBNNe"] = PROBNNe(e1)
             CandidateInfo["e2PROBNNe"]= PROBNNe(e2)
             CandidateInfo["e1PROBNNghost"]=PROBNNghost(e1)
             CandidateInfo["e2PROBNNghost"]=PROBNNghost(e2)
             CandidateInfo["pi1PROBNNghost"]=PROBNNghost(pi1)
             CandidateInfo["pi2PROBNNghost"]=PROBNNghost(pi2)
             CandidateInfo["e1GP"] = TRGHOSTPROB(e1)
             CandidateInfo["e2GP"] = TRGHOSTPROB(e2)
             CandidateInfo["pi1GP"] = TRGHOSTPROB(pi1)
             CandidateInfo["pi2GP"] = TRGHOSTPROB(pi2)

             
             
             keys = CandidateInfo.keys()
             keys.sort()
             for key in keys:
                 mytup1.column(key,CandidateInfo[key])
             mytup1.write()
        return SUCCESS



