#import numpy

#if isCondor:sys.path.append('ExoPieUtils/commonutils/')
import sys 
sys.path.append('../ExoPieUtils/commonutils/')
import MathUtils as mathutil
from MathUtils import *

'''
## all these functions are present in the mathutils, do mathutils import, once Deepak has fixed the condor setup 
def getP3(px_, py_, pz_):
    return( numpy.sqrt( px_**2 + py_**2 + pz_**2) )
def Phi_mpi_pi(x):
    kPI = 3.14159265358979323846
    kTWOPI = 2 * kPI

    while (x >= kPI): x = x - kTWOPI;
    while (x < -kPI): x = x + kTWOPI;
    return x;

def getPt(px_, py_):
    return  numpy.sqrt( px_**2 + py_**2)

def getEta(px_, py_, pz_):
    p3_   = getP3(px_, py_, pz_)
    return( numpy.log((p3_ + pz_)/(p3_ - pz_))/2)

def getPhi(px_, py_):
    return( numpy.arctan2( py_, px_))

def DeltaPhi(phi1,phi2):
   phi = Phi_mpi_pi(phi1-phi2)

   return abs(phi)

def Delta_R(eta1, eta2, phi1,phi2):
    deltaeta = eta1-eta2
    deltaphi = DeltaPhi(phi1,phi2)
    DR = TMath.Sqrt ( deltaeta**2 + deltaphi**2 )
    return DR
'''
def GenPtProducer(sample,nGenPar, genParId, genMomParId, genParSt,st_genParPx,st_genParPy):
    pt_list=[]
    #################
    # WJets
    #################
    if sample==24:
        goodLepID = []
        for ig in range(nGenPar):
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]
            if ( (abs(PID) != 11) & (abs(PID) != 12) &  (abs(PID) != 13) & (abs(PID) != 14) &  (abs(PID) != 15) &  (abs(PID) != 16) ): continue
            if ( ( (status != 1) & (abs(PID) != 15)) | ( (status != 2) & (abs(PID) == 15)) ): continue
            if ( (abs(momPID) != 24) & (momPID != PID) ): continue
            goodLepID.append(ig)

        if len(goodLepID) == 2 :
            pt_list.append(getPt((st_genParPx[goodLepID[0]]+st_genParPx[goodLepID[1]]),(st_genParPy[goodLepID[0]]+st_genParPy[goodLepID[1]])))
    #################
    #ZJets
    #################
    if sample == 23:
        goodLepID = []
        for ig in range(nGenPar):
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]


            if ( (abs(PID) != 12) &  (abs(PID) != 14) &  (abs(PID) != 16) ) and ( (abs(PID) != 11) &  (abs(PID) != 13) &  (abs(PID) != 15) ): continue
            if ( status != 1 ) : continue
            if ( (momPID != 23) & (momPID != PID) ) : continue
            goodLepID.append(ig)

        if len(goodLepID) == 2 :
            pt_list.append(getPt((st_genParPx[goodLepID[0]]+st_genParPx[goodLepID[1]]),(st_genParPy[goodLepID[0]]+st_genParPy[goodLepID[1]])))
    #################
    #TTBar
    #################
    if (sample==6):
        goodLepID = []
        for ig in range(nGenPar):
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]
            if ( abs(PID) == 6) :
                goodLepID.append(ig)
        if(len(goodLepID)==2):
            pt_list.append(getPt(st_genParPx[goodLepID[0]],st_genParPy[goodLepID[0]]))
            pt_list.append(getPt(st_genParPx[goodLepID[1]],st_genParPy[goodLepID[1]]))

    return pt_list

''' algo for the function 


1. find the top i.e. pdgid = 6 
2. check what is the daughter: 
  - if W boson then: 
      - check what is the daughter: 
           - if two quarks: 
               - check if both q match with the AK8 jet within DR = 1.0 
           - if one lepton and one neutrino: 
               - then just let it go. 
'''

def GenMatchTop(sample,nGenPar, genParId, genMomParId, genParSt,st_genParPx,st_genParPy,st_genParPz, st_AK8jetpx, st_AK8jetpy, st_AK8jetpz):
    topmatchStr = 1
    Windex=[]
    Topindex=[]
    Wdaughter = []
    WhadID = []
    b_index_tophad=[]
    if (sample==6):
        goodLepID = []
        for ig in range(nGenPar):
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]
            #print " PID, momPID, status", genParId[ig], genMomParId[ig], genParSt[ig]
            ## save the W index from the vector
            
            if (abs(PID) == 6): Topindex.append(ig)
            
            if (abs(PID) ==24): Windex.append(ig)
            
            ## this is to get the sign of W boson so that b jet mother can be found with proper sign (i.e. t or tbar) 
            if ( (abs(PID) <=6) and abs(momPID) == 24) :
                Wdaughter.append(ig)
                WhadID.append(momPID)
                
        
        b_mom_id = -9999
        if WhadID[0] == 24: b_mom_id = 6
        if WhadID[0] == -24: b_mom_id = -6
        
        ## this can't be done without looping again on the gen particles 
        ## getting the correct b-jet from top0hadronic (not from leptonic one). 
        for ig in range(nGenPar):
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            if ( abs(PID) == 5 and momPID == b_mom_id ): 
                b_index_tophad.append(ig)
                break;
        
        
        st_genParEta = getEta(st_genParPx, st_genParPy, st_genParPz)
        st_genParPhi = getPhi(st_genParPx, st_genParPy)
        
        
        
        daughter_eta = [st_genParEta[id_] for id_ in Wdaughter ]
        daughter_phi = [st_genParPhi[id_] for id_ in Wdaughter ]
        
        fjeta        = getEta(st_AK8jetpx, st_AK8jetpy, st_AK8jetpz)
        fjphi        = getPhi(st_AK8jetpx, st_AK8jetpy)
        
        
        topeta       = [st_genParEta[id_] for id_ in Topindex ]
        topphi       = [st_genParPhi[id_] for id_ in Topindex ]
        bjeteta      = st_genParEta[b_index_tophad[0]]
        bjetphi      = st_genParPhi[b_index_tophad[0]]
        
        dr_daughters = Delta_R(daughter_eta[0], daughter_eta[1],  daughter_phi[0], daughter_phi[1])
        dr_ak8_dau0 = Delta_R(daughter_eta[0], fjeta, daughter_phi[0], fjphi)
        dr_ak8_dau1 = Delta_R(daughter_eta[1], fjeta, daughter_phi[1], fjphi)
        
        dr_b_AK8  = Delta_R(bjeteta, fjeta, bjetphi, fjphi)

        
        if dr_daughters < 0.8 and dr_ak8_dau0 < 0.8 and dr_ak8_dau1 < 0.8  and dr_b_AK8 < 0.8:
            topmatchStr = 2
        elif dr_daughters < 0.8 and dr_ak8_dau0 < 0.8 and dr_ak8_dau1 < 0.8 :
            topmatchStr = 3
        else: topmatchStr = 4

        
        
        print "daughter_eta, daughter_phi, fjeta, fjphi ", daughter_eta, daughter_phi, fjeta, fjphi
        print "dr_daughters, dr_ak8_dau0, dr_ak8_dau1, dr_b_AK8",dr_daughters, dr_ak8_dau0, dr_ak8_dau1, dr_b_AK8
    return topmatchStr



