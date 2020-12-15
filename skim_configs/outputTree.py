#!/usr/bin/env python
from ROOT import TFile, TTree, TH1F, TH1D, TH1, TCanvas, TChain, TGraphAsymmErrors, TMath, TH2D, TLorentzVector, AddressOf, gROOT, TNamed
import ROOT as ROOT
import os
import traceback
import sys
import optparse
import argparse
from array import array
import math
import numpy as numpy
import pandas
from root_pandas import read_root
from pandas import DataFrame, concat
from pandas import Series
import time

'''
outfilenameis=(open('configs/outfilename.txt')).readline()

print "outfilenameis = ",outfilenameis

outfile = TFile(outfilenameis,'RECREATE')

outTree = TTree( 'outTree', 'tree branches' )
'''

st_runId = numpy.zeros(1, dtype=int)
st_lumiSection = array('L', [0])
st_eventId = array('L', [0])
st_isData = array('b', [0])

st_isak4JetBasedHemEvent = array('b', [0])
st_isak8JetBasedHemEvent = array('b', [0])
st_ismetphiBasedHemEvent1 = array('b', [0])
st_ismetphiBasedHemEvent2 = array('b', [0])

st_prefiringweight = array('f', [0.])
st_prefiringweightup = array('f', [0.])
st_prefiringweightdown = array('f', [0.])

st_eletrigdecision = array('b', [0])
st_mutrigdecision = array('b', [0])
st_mettrigdecision = array('b', [0])
st_photrigdecision = array('b', [0])
st_filterstatus = array('b', [0])

st_pfMetSmearPt = array('f', [0.])
st_pfMetCorrPt = array('f', [0.])
st_pfMetCorrPhi = array('f', [0.])
st_pfMetCorrSig = array('f', [0.])
st_pfpatCaloMETPt = array('f', [0.])
st_pfpatCaloMETPhi = array('f', [0.])
st_pfTRKMETPt = array('f', [0.])
st_pfTRKMETPhi = array('f', [0.])
st_pfMetUncJetResUp = ROOT.std.vector('float')()
st_pfMetUncJetResDown = ROOT.std.vector('float')()
st_pfMetUncJetEnUp = ROOT.std.vector('float')()
st_pfMetUncJetEnDown = ROOT.std.vector('float')()
## add calo met
## add modified met

## now we have only one flag for one object trigger
st_eleTrig = array('b', [0])
st_muTrig = array('b', [0])
st_metTrig = array('b', [0])
st_phoTrig = array('b', [0])

st_filterStatus = ROOT.std.vector('bool')()
st_filters = ROOT.std.vector(ROOT.std.string)()

st_TopMatching = array('L', [0])  # ROOT.std.vector('int')()


st_THINnJet = array('L', [0])  # ROOT.std.vector('int')()
st_THINjetPx = ROOT.std.vector('float')()
st_THINjetPy = ROOT.std.vector('float')()
st_THINjetPz = ROOT.std.vector('float')()
st_THINjetEnergy = ROOT.std.vector('float')()
st_THINjetDeepCSV = ROOT.std.vector('float')()
st_THINjetHadronFlavor = ROOT.std.vector('int')()
st_THINjetCEmEF = ROOT.std.vector('float')()
st_THINjetCHadEF = ROOT.std.vector('float')()
st_THINjetNEmEF = ROOT.std.vector('float')()
st_THINjetNHadEF = ROOT.std.vector('float')()
st_THINjetCMulti = ROOT.std.vector('float')()
st_THINjetNMultiplicity = ROOT.std.vector('float')()
st_THINjetCorrUnc = ROOT.std.vector('float')()
st_THINPUjetIDLoose = ROOT.std.vector('bool')()
st_THINPUjetIDMedium = ROOT.std.vector('bool')()
st_THINPUjetIDTight = ROOT.std.vector('bool')()

st_THINbRegNNResolution = ROOT.std.vector('float')()
st_THINbRegNNCorr = ROOT.std.vector('float')()

st_nfjet = array('L', [0])
st_fjetPx = ROOT.std.vector('float')()
st_fjetPy = ROOT.std.vector('float')()
st_fjetPz = ROOT.std.vector('float')()
st_fjetEnergy = ROOT.std.vector('float')()
st_fjetDoubleSV = ROOT.std.vector('float')()
st_fjetProbQCDb = ROOT.std.vector('float')()
st_fjetProbHbb = ROOT.std.vector('float')()
st_fjetProbQCDc = ROOT.std.vector('float')()
st_fjetProbHcc = ROOT.std.vector('float')()
st_fjetProbHbbc = ROOT.std.vector('float')()
st_fjetProbbbvsLight = ROOT.std.vector('float')()
st_fjetProbccvsLight = ROOT.std.vector('float')()
st_fjetProbTvsQCD = ROOT.std.vector('float')()
st_fjetProbWvsQCD = ROOT.std.vector('float')()
st_fjetProbZHbbvsQCD = ROOT.std.vector('float')()
st_fjetSDMass = ROOT.std.vector('float')()
st_fjetSDMassCorrFact = ROOT.std.vector('float')()
st_fjetN2b1 = ROOT.std.vector('float')()
st_fjetN2b2 = ROOT.std.vector('float')()
st_fjetTau21 = ROOT.std.vector('float')()
st_fjetCHSPRMass = ROOT.std.vector('float')()
st_fjetCHSSDMass = ROOT.std.vector('float')()


st_nEle = array('L', [0])  # ROOT.std.vector('int')()
st_elePx = ROOT.std.vector('float')()
st_elePy = ROOT.std.vector('float')()
st_elePz = ROOT.std.vector('float')()
st_eleEnergy = ROOT.std.vector('float')()
st_eleIsPassLoose = ROOT.std.vector('bool')()
st_eleIsPassTight = ROOT.std.vector('bool')()
st_eleCharge = ROOT.std.vector('float')()


st_nPho = array('L', [0])  # ROOT.std.vector('int')()
st_phoPx = ROOT.std.vector('float')()
st_phoPy = ROOT.std.vector('float')()
st_phoPz = ROOT.std.vector('float')()
st_phoEnergy = ROOT.std.vector('float')()
st_phoIsPassTight = ROOT.std.vector('bool')()

st_nMu = array('L', [0])  # ROOT.std.vector('int')()
st_muPx = ROOT.std.vector('float')()
st_muPy = ROOT.std.vector('float')()
st_muPz = ROOT.std.vector('float')()
st_muEnergy = ROOT.std.vector('float')()
st_isTightMuon = ROOT.std.vector('bool')()
st_muCharge = ROOT.std.vector('float')()
#st_muIso              = ROOT.std.vector('float')()
'''
st_HPSTau_n            = array( 'L', [ 0 ] ) #ROOT.std.vector('int')()
st_nTauTightElectron   = array( 'L', [ 0 ] )
st_nTauTightMuon       = array( 'L', [ 0 ] )
st_nTauTightEleMu      = array( 'L', [ 0 ] )
st_nTauLooseEleMu      = array( 'L', [ 0 ] )
st_Taudisc_againstLooseMuon       = ROOT.std.vector('bool')()
st_Taudisc_againstTightMuon      = ROOT.std.vector('bool')()
st_Taudisc_againstLooseElectron   = ROOT.std.vector('bool')()
st_Taudisc_againstMediumElectron  = ROOT.std.vector('bool')()
st_tau_isoLoose        = ROOT.std.vector('bool')()
st_tau_isoMedium       = ROOT.std.vector('bool')()
st_tau_isoTight        = ROOT.std.vector('bool')()
st_tau_dm              = ROOT.std.vector('bool')()
'''
## add against mu and against mu loose and medium WP

st_nTau_DRBased_EleMuVeto = array('L', [0])
st_nTau_discBased_looseElelooseMuVeto = array('L', [0])
st_nTau_discBased_looseEleTightMuVeto = array('L', [0])
st_nTau_discBased_mediumElelooseMuVeto = array('L', [0])
st_nTau_discBased_TightElelooseMuVeto = array('L', [0])
st_nTau_discBased_TightEleTightMuVeto = array('L', [0])

mcweight = array('f', [0])
st_pu_nTrueInt = array('f', [0])  # ROOT.std.vector('std::vector<float>')()
st_pu_nPUVert = array('f', [0])
st_THINjetNPV = array('f', [0])  # ROOT.std.vector('std::vector<float>')()

# st_nGenPar             = array( 'L', [ 0 ] )
# st_genParId            = ROOT.std.vector('int')()
# st_genMomParId         = ROOT.std.vector('int')()
# st_genParSt            = ROOT.std.vector('int')()
# st_genParPx            = ROOT.std.vector('float')()
# st_genParPy            = ROOT.std.vector('float')()
# st_genParPz            = ROOT.std.vector('float')()
# st_genParEnergy        = ROOT.std.vector('float')()
st_genParPt = ROOT.std.vector('float')()
st_genParSample = ROOT.std.vector('int')()
st_METXYCorr_Met_MetPhi = ROOT.std.vector('float')()


WenuRecoil = array('f', [0.])
Wenumass = array('f', [0.])
WenuPhi = array('f', [0.])

WmunuRecoil = array('f', [0.])
Wmunumass = array('f', [0.])
WmunuPhi = array('f', [0.])

ZeeRecoil = array('f', [0.])
ZeeMass = array('f', [0.])
ZeePhi = array('f', [0.])

ZmumuRecoil = array('f', [0.])
ZmumuMass = array('f', [0.])
ZmumuPhi = array('f', [0.])

GammaRecoil = array('f', [0.])
GammaPhi = array('f', [0.])
'''
outTree.Branch( 'st_runId', st_runId , 'st_runId/L')
outTree.Branch( 'st_lumiSection', st_lumiSection , 'st_lumiSection/L')
outTree.Branch( 'st_eventId',  st_eventId, 'st_eventId/L')
outTree.Branch( 'st_pfMetCorrPt', st_pfMetCorrPt , 'st_pfMetCorrPt/F')
outTree.Branch( 'st_pfMetCorrPhi', st_pfMetCorrPhi , 'st_pfMetCorrPhi/F')
outTree.Branch( 'st_pfMetUncJetResUp', st_pfMetUncJetResUp)
outTree.Branch( 'st_pfMetUncJetResDown', st_pfMetUncJetResDown)
outTree.Branch( 'st_pfMetUncJetEnUp', st_pfMetUncJetEnUp )
outTree.Branch( 'st_pfMetUncJetEnDown', st_pfMetUncJetEnDown)
outTree.Branch( 'st_isData', st_isData , 'st_isData/O')

        #for trigs in triglist:
        #    exec("outTree.Branch( 'st_"+trigs+"', st_"+trigs+" , 'st_"+trigs+"/O')")

outTree.Branch( 'st_THINnJet',st_THINnJet, 'st_THINnJet/L' )
outTree.Branch( 'st_THINjetPx', st_THINjetPx  )
outTree.Branch( 'st_THINjetPy' , st_THINjetPy )
outTree.Branch( 'st_THINjetPz', st_THINjetPz )
outTree.Branch( 'st_THINjetEnergy', st_THINjetEnergy )
outTree.Branch( 'st_THINjetDeepCSV',st_THINjetDeepCSV )
outTree.Branch( 'st_THINjetHadronFlavor',st_THINjetHadronFlavor )
outTree.Branch( 'st_THINjetNHadEF',st_THINjetNHadEF )
outTree.Branch( 'st_THINjetCHadEF',st_THINjetCHadEF )

outTree.Branch( 'st_THINjetCEmEF',st_THINjetCEmEF )
outTree.Branch( 'st_THINjetPhoEF',st_THINjetPhoEF )
outTree.Branch( 'st_THINjetEleEF',st_THINjetEleEF )
outTree.Branch( 'st_THINjetMuoEF',st_THINjetMuoEF )
outTree.Branch('st_THINjetCorrUnc', st_THINjetCorrUnc)


outTree.Branch( 'st_nfjet',st_nfjet,'st_nfjet/L')
outTree.Branch( 'st_fjetPx',st_fjetPx)
outTree.Branch( 'st_fjetPy',st_fjetPy)
outTree.Branch( 'st_fjetPz',st_fjetPz)
outTree.Branch( 'st_fjetEnergy',st_fjetEnergy)
outTree.Branch( 'st_fjetDoubleSV',st_fjetDoubleSV)
outTree.Branch( 'st_fjetProbQCDb',st_fjetProbQCDb)
outTree.Branch( 'st_fjetProbHbb',st_fjetProbHbb)
outTree.Branch( 'st_fjetProbQCDc',st_fjetProbQCDc)
outTree.Branch( 'st_fjetProbHcc',st_fjetProbHcc)
outTree.Branch( 'st_fjetProbHbbc',st_fjetProbHbbc)
outTree.Branch( 'st_fjetProbbbvsLight',st_fjetProbbbvsLight)
outTree.Branch( 'st_fjetProbccvsLight',st_fjetProbccvsLight)
outTree.Branch( 'st_fjetProbTvsQCD',st_fjetProbTvsQCD)
outTree.Branch( 'st_fjetProbWvsQCD',st_fjetProbWvsQCD)
outTree.Branch( 'st_fjetProbZHbbvsQCD',st_fjetProbZHbbvsQCD)
outTree.Branch( 'st_fjetSDMass',st_fjetSDMass)
outTree.Branch( 'st_fjetN2b1',st_fjetN2b1)
outTree.Branch( 'st_fjetN2b2',st_fjetN2b2)
outTree.Branch( 'st_fjetCHSPRMass',st_fjetCHSPRMass)
outTree.Branch( 'st_fjetCHSSDMass',st_fjetCHSSDMass)



outTree.Branch( 'st_nEle',st_nEle , 'st_nEle/L')
outTree.Branch( 'st_elePx', st_elePx  )
outTree.Branch( 'st_elePy' , st_elePy )
outTree.Branch( 'st_elePz', st_elePz )
outTree.Branch( 'st_eleEnergy', st_eleEnergy )
outTree.Branch( 'st_eleIsPassTight', st_eleIsPassTight)#, 'st_eleIsPassTight/O' )
outTree.Branch( 'st_eleIsPassLoose', st_eleIsPassLoose)#, 'st_eleIsPassLoose/O' )

outTree.Branch( 'st_nPho',st_nPho , 'st_nPho/L')
outTree.Branch( 'st_phoIsPassTight', st_phoIsPassTight)#, 'st_phoIsPassTight/O' )
outTree.Branch( 'st_phoPx', st_phoPx  )
outTree.Branch( 'st_phoPy' , st_phoPy )
outTree.Branch( 'st_phoPz', st_phoPz )
outTree.Branch( 'st_phoEnergy', st_phoEnergy )


outTree.Branch( 'st_nMu',st_nMu , 'st_nMu/L')
outTree.Branch( 'st_muPx', st_muPx)
outTree.Branch( 'st_muPy' , st_muPy)
outTree.Branch( 'st_muPz', st_muPz)
outTree.Branch( 'st_muEnergy', st_muEnergy)
outTree.Branch( 'st_isTightMuon', st_isTightMuon)#, 'st_isTightMuon/O' )
        #outTree.Branch( 'st_muIso', st_muIso)#, 'st_muIso/F')

outTree.Branch( 'st_HPSTau_n', st_HPSTau_n, 'st_HPSTau_n/L')
outTree.Branch( 'st_nTauTightElectron', st_nTauTightElectron, 'st_nTauTightElectron/L')
outTree.Branch( 'st_nTauTightMuon', st_nTauTightMuon, 'st_nTauTightMuon/L')
outTree.Branch( 'st_nTauTightEleMu', st_nTauTightEleMu, 'st_nTauTightEleMu/L')
outTree.Branch( 'st_nTauLooseEleMu', st_nTauLooseEleMu, 'st_nTauLooseEleMu/L')

outTree.Branch( 'st_pu_nTrueInt', st_pu_nTrueInt, 'st_pu_nTrueInt/F')
outTree.Branch( 'st_pu_nPUVert', st_pu_nPUVert, 'st_pu_nPUVert/F')
outTree.Branch( 'st_THINjetNPV', st_THINjetNPV, 'st_THINjetNPV/F')
outTree.Branch( 'mcweight', mcweight, 'mcweight/F')
outTree.Branch( 'st_nGenPar',st_nGenPar,'st_nGenPar/L' )  #nGenPar/I
outTree.Branch( 'st_genParId',st_genParId )  #vector<int>
outTree.Branch( 'st_genMomParId',st_genMomParId )
outTree.Branch( 'st_genParSt',st_genParSt )
outTree.Branch( 'st_genParPx', st_genParPx  )
outTree.Branch( 'st_genParPy' , st_genParPy )
outTree.Branch( 'st_genParPz', st_genParPz )
outTree.Branch( 'st_genParEnergy', st_genParEnergy )

outTree.Branch( 'WenuRecoil', WenuRecoil, 'WenuRecoil/F')
outTree.Branch( 'Wenumass', Wenumass, 'Wenumass/F')
outTree.Branch( 'WenuPhi', WenuPhi, 'WenuPhi/F')

outTree.Branch( 'WmunuRecoil', WmunuRecoil, 'WmunuRecoil/F')
outTree.Branch( 'Wmunumass', Wmunumass, 'Wmunumass/F')
outTree.Branch( 'WmunuPhi', WmunuPhi, 'WmunuPhi/F')

outTree.Branch( 'ZeeRecoil', ZeeRecoil, 'ZeeRecoil/F')
outTree.Branch( 'ZeeMass', ZeeMass, 'ZeeMass/F')
outTree.Branch( 'ZeePhi', ZeePhi, 'ZeePhi/F')

outTree.Branch( 'ZmumuRecoil', ZmumuRecoil, 'ZmumuRecoil/F')
outTree.Branch( 'ZmumuMass', ZmumuMass, 'ZmumuMass/F')
outTree.Branch( 'ZmumuPhi', ZmumuPhi, 'ZmumuPhi/F')

outTree.Branch( 'GammaRecoil', GammaRecoil, 'GammaRecoil/F')
outTree.Branch( 'GammaPhi', GammaPhi, 'GammaPhi/F')

'''
