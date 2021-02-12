#!/usr/bin/env python
from ROOT import TFile, TTree, TH1F, TH1D, TH1, TCanvas, TChain, TGraphAsymmErrors, TMath, TH2D, TLorentzVector, AddressOf, gROOT, TNamed
import ROOT as ROOT
import os,traceback
import sys, optparse,argparse
from array import array
import math
import numpy as numpy
import pandas
from root_pandas import read_root
from pandas import  DataFrame, concat
from pandas import Series
import time
import glob

## for parallel threads in interactive running
from multiprocessing import Process
import multiprocessing as mp


isCondor = False

## user packages
## in local dir
sys.path.append('skim_configs')
import  triggers as trig
import variables as branches
import filters as filters
#import genPtProducer as GenPtProd

## from commonutils
if isCondor:sys.path.append('ExoPieUtils/commonutils/')
else:sys.path.append('../ExoPieUtils/commonutils/')
import MathUtils as mathutil
from MathUtils import *
import BooleanUtils as boolutil


## from analysisutils
if isCondor:sys.path.append('ExoPieUtils/analysisutils/')
else:sys.path.append('../ExoPieUtils/analysisutils/')
import analysis_utils as anautil
import genPtProducer as GenPtProd
######################################################################################################
## All import are done before this
######################################################################################################


runInteractive = False
runOn2016 = False
runOn2017 = False
runOn2018 = False

## ----- start if clock

start = time.clock()


## ----- command line argument
usage = "analyzer for bb+DM (debugging) "
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-i", "--inputfile",  dest="inputfile", default="myfiles.txt")
parser.add_argument("-inDir", "--inputDir",  dest="inputDir", default=".")
parser.add_argument("-runOnTXT", "--runOnTXT", action="store_true", dest="runOnTXT")
parser.add_argument("-o", "--outputfile", dest="outputfile", default="out.root")
parser.add_argument("-D", "--outputdir", dest="outputdir")
parser.add_argument("-F", "--farmout", action="store_true",  dest="farmout")
parser.add_argument("-y", "--year", dest="year", default="Year")
parser.add_argument("--monoh_zpb", action="store_true", dest="monoh_zpb")
parser.add_argument("--bbdm_2hdma", action="store_true", dest="bbdm_2hdma")
parser.add_argument("--bbDM_DMSimp", action="store_true", dest="bbDM_DMSimp")
parser.add_argument("--mA", dest="mA_", default="0")
parser.add_argument("--ma", dest="ma_", default="0")

#parser.set_defaults(runOnTXT=False)
## add argument for debug, default to be false

args = parser.parse_args()

if args.farmout == None:
    isfarmout = False
else:
    isfarmout = args.farmout

if args.inputDir and isfarmout:
    dirName = args.inputDir

if args.year == '2016':
    runOn2016 = True
elif args.year == '2017':
    runOn2017 = True
elif args.year == '2018':
    runOn2018 = True
else:
    print('Please provide on which year you want to run?')
    sys.exit()

runOnTxt = False
if args.runOnTXT:
    runOnTxt = True

if isfarmout:
    infile = args.inputfile

else:
    print "No file is provided for farmout"


outputdir = '.'
if args.outputdir:
    outputdir = str(args.outputdir)

infilename = "ExoPieElementTuples.root"

debug_ = False

if runOn2016 or runOn2017 or runOn2018:
    from TheaCorrection import TheaCorrection_2016 as TheaCorrection

if runOn2016:
    filter_list = filters.filters2016
elif runOn2017:
    filter_list = filters.filters2017
elif runOn2018:
    filter_list = filters.filters2018

'''
elif runOn2017:
    from TheaCorrection import TheaCorrection_2017 as TheaCorrection
elif runOn2018:
    from TheaCorrection import TheaCorrection_2018 as TheaCorrection
'''
makeStr = ''
monoh_zpb = False
if args.monoh_zpb:
    monoh_zpb = True
    mA_ = args.mA_
    ma_ = args.ma_
    makeStr = "_Zpb"+str(mA_)

bbdm_2hdma = False
if args.bbdm_2hdma:
    bbdm_2hdma = True
    mA_ = args.mA_
    ma_ = args.ma_
    makeStr = "_ma_"+str(ma_)+"_mA_"+str(mA_)

bbDM_DMSimp = False
if args.bbDM_DMSimp:
    bbDM_DMSimp = True
    mA_ = args.mA_
    ma_ = args.ma_
    makeStr = "_MPhi"+str(mA_)

ROOT.gROOT.ProcessLine('.L skim_configs/XYMETCorrection.cc+')

def whichsample(filename):
    print "SkimTree:whichsample:-- file name is ", filename
    sample = -999
    if "TTT" in filename:
        sample = 6
    elif "WJetsToLNu_HT" in filename:
        sample = 24
    elif "ZJetsToNuNu_HT" in filename or "DYJetsToLL" in filename:
        sample = 23
    return sample


def TextToList(textfile):
    return([iline.rstrip() for iline in open(textfile)])

## the input file list and key is caught in one variable as a python list,
#### first element is the list of rootfiles
#### second element is the key, user to name output.root


def jetID_(jetCEmEF, jetCHadEF, jetNEmEF, jetNHadEF, jetCMulti, jetNMultiplicity, Jet_eta):
    NumConst_ = jetCMulti+jetNMultiplicity
    if (abs(Jet_eta) <= 2.7):
        looseJetID_2016 = (jetNHadEF < 0.99 and jetNEmEF < 0.99 and NumConst_ > 1) and (
            (abs(Jet_eta) <= 2.4 and jetCHadEF > 0 and jetCMulti > 0 and jetCEmEF < 0.99) or abs(Jet_eta) > 2.4) and abs(Jet_eta) <= 2.7
        tightJetID_2017 = (jetNHadEF < 0.90 and jetNEmEF < 0.90 and NumConst_ > 1) and (
            (abs(Jet_eta) <= 2.4 and jetCHadEF > 0 and jetCMulti > 0) or abs(Jet_eta) > 2.4) and abs(Jet_eta) <= 2.7
    elif (abs(Jet_eta) > 2.7 and abs(Jet_eta) <= 3.0):
        looseJetID_2016 = (jetNHadEF < 0.98 and jetNEmEF > 0.01 and jetNMultiplicity > 2 and abs(
            Jet_eta) > 2.7 and abs(Jet_eta) <= 3.0)
        tightJetID_2017 = (jetNEmEF < 0.99 and jetNEmEF > 0.02 and jetNMultiplicity > 2 and abs(
            Jet_eta) > 2.7 and abs(Jet_eta) <= 3.0)
    elif (abs(Jet_eta) > 3.0):
        looseJetID_2016 = (
            jetNEmEF < 0.90 and jetNMultiplicity > 10 and abs(Jet_eta) > 3.0)
        tightJetID_2017 = (jetNEmEF < 0.90 and jetNHadEF >
                           0.02 and jetNMultiplicity > 10 and abs(Jet_eta) > 3.0)
    return looseJetID_2016, tightJetID_2017


def runbbdm(txtfile):
    infile_ = []
    outfilename = ""
    prefix = "Skimmed_"
    ikey_ = ""

    if not runInteractive:
        print "running for ", txtfile
        infile_ = TextToList(txtfile)
        outfile = txtfile.split('/')[-1].replace('.txt', makeStr+'.root')
        #key_=txtfile[1]

        ''' old
        prefix="Skimmed_"
        outfilename= prefix+infile_.split("/")[-1]
        '''

        outfilename = outfile  # prefix+key_+".root"
        print "outfilename", outfilename

    if runInteractive:
        infile_ = TextToList(txtfile)
        print "infile_ = ", infile_
        #print "running code for ",infile_
        prefix_ = ''  # '/eos/cms/store/group/phys_exotica/bbMET/2017_skimmedFiles/locallygenerated/'
        if outputdir != '.':
            prefix_ = outputdir+'/'
        #print "prefix_", prefix_
        outfilename = prefix_ + \
            txtfile.split('/')[-1].replace('.txt', makeStr+'.root')
        print 'outfilename',  outfilename

    samplename = whichsample(outfilename)
    print "samplename = ", samplename

    #outputfilename = args.outputfile
    h_total = TH1F('h_total', 'h_total', 2, 0, 2)
    h_total_mcweight = TH1F('h_total_mcweight', 'h_total_mcweight', 2, 0, 2)

    if runOn2016:
        triglist = trig.trigger2016
        eletrig = trig.Electrontrigger2016
        muontrig = trig.Muontrigger2016
        mettrig = trig.METtrigger2016
        photontrig = trig.Photontrigger2016
    elif runOn2017:
        triglist = trig.trigger2017
        eletrig = trig.Electrontrigger2017
        muontrig = trig.Muontrigger2017
        mettrig = trig.METtrigger2017
        photontrig = trig.Photontrigger2017
    elif runOn2018:
        triglist = trig.trigger2018
        eletrig = trig.Electrontrigger2018
        muontrig = trig.Muontrigger2018
        mettrig = trig.METtrigger2018
        photontrig = trig.Photontrigger2018
    passfilename = open("skim_configs/outfilename.txt", "w")

    passfilename.write(outfilename)
    passfilename.close()

    ## this will give some warning, but that is safe,
    from outputTree import *

    ## following can be moved to outputtree.py if we manage to change the name of output root file.
    outfilenameis = outfilename
    outfile = TFile(outfilenameis, 'RECREATE')
    outTree = TTree('outTree', 'tree branches')
    outTree.Branch('st_runId', st_runId, 'st_runId/L')
    outTree.Branch('st_lumiSection', st_lumiSection, 'st_lumiSection/L')
    outTree.Branch('st_eventId',  st_eventId, 'st_eventId/L')
    outTree.Branch('st_prefiringweight', st_prefiringweight,'st_prefiringweight/F')
    outTree.Branch('st_prefiringweightup', st_prefiringweightup, 'st_prefiringweightup/F')
    outTree.Branch('st_prefiringweightdown', st_prefiringweightdown, 'st_prefiringweightdown/F')
    outTree.Branch('st_pfMetSmearPt', st_pfMetSmearPt, 'st_pfMetSmearPt/F')
    outTree.Branch('st_pfMetCorrPt', st_pfMetCorrPt, 'st_pfMetCorrPt/F')
    outTree.Branch('st_pfMetCorrPhi', st_pfMetCorrPhi, 'st_pfMetCorrPhi/F')
    outTree.Branch('st_pfMetCorrSig', st_pfMetCorrSig, 'st_pfMetCorrSig/F')
    outTree.Branch('st_METXYCorr_Met', st_METXYCorr_Met, 'st_METXYCorr_Met/F')
    outTree.Branch('st_METXYCorr_MetPhi', st_METXYCorr_MetPhi, 'st_METXYCorr_MetPhi/F')
    outTree.Branch('st_pfpatCaloMETPt', st_pfpatCaloMETPt, 'st_pfpatCaloMETPt/F')
    outTree.Branch('st_pfpatCaloMETPhi', st_pfpatCaloMETPhi, 'st_pfpatCaloMETPhi/F')
    outTree.Branch('st_pfTRKMETPt', st_pfTRKMETPt, 'st_pfTRKMETPt/F')
    outTree.Branch('st_pfTRKMETPhi', st_pfTRKMETPhi, 'st_pfTRKMETPhi/F')
    outTree.Branch('st_scaleWeightUP', st_scaleWeightUP, 'st_scaleWeightUP/F')
    outTree.Branch('st_scaleWeightDOWN', st_scaleWeightDOWN, 'st_scaleWeightDOWN/F')
    outTree.Branch('st_pdfWeightUP', st_pdfWeightUP, 'st_pdfWeightUP/F')
    outTree.Branch('st_pdfWeightDOWN', st_pdfWeightDOWN, 'st_pdfWeightDOWN/F')
    outTree.Branch('st_pfMetUncJetResUp', st_pfMetUncJetResUp)
    outTree.Branch('st_pfMetUncJetResDown', st_pfMetUncJetResDown)
    outTree.Branch('st_pfMetUncJetEnUp', st_pfMetUncJetEnUp)
    outTree.Branch('st_pfMetUncJetEnDown', st_pfMetUncJetEnDown)
    outTree.Branch('st_isData', st_isData, 'st_isData/O')

    outTree.Branch('st_isak4JetBasedHemEvent', st_isak4JetBasedHemEvent, 'st_isak4JetBasedHemEvent/O')
    outTree.Branch('st_isak8JetBasedHemEvent', st_isak8JetBasedHemEvent, 'st_isak8JetBasedHemEvent/O')
    outTree.Branch('st_ismetphiBasedHemEvent1', st_ismetphiBasedHemEvent1, 'st_ismetphiBasedHemEvent1/O')
    outTree.Branch('st_ismetphiBasedHemEvent2', st_ismetphiBasedHemEvent2, 'st_ismetphiBasedHemEvent2/O')

    outTree.Branch('st_THINnJet', st_THINnJet, 'st_THINnJet/L')
    outTree.Branch('st_THINjetPx', st_THINjetPx)
    outTree.Branch('st_THINjetPy', st_THINjetPy)
    outTree.Branch('st_THINjetPz', st_THINjetPz)
    outTree.Branch('st_THINjetEnergy', st_THINjetEnergy)
    outTree.Branch('st_THINjetDeepCSV', st_THINjetDeepCSV)
    outTree.Branch('st_THINjetHadronFlavor', st_THINjetHadronFlavor)
    outTree.Branch('st_THINjetNHadEF', st_THINjetNHadEF)
    outTree.Branch('st_THINjetCHadEF', st_THINjetCHadEF)

    outTree.Branch('st_THINjetCEmEF', st_THINjetCEmEF)
    # outTree.Branch( 'st_THINjetPhoEF',st_THINjetPhoEF )
    # outTree.Branch( 'st_THINjetEleEF',st_THINjetEleEF )
    # outTree.Branch( 'st_THINjetMuoEF',st_THINjetMuoEF )
    outTree.Branch('st_THINjetNEmEF', st_THINjetNEmEF)
    outTree.Branch('st_THINjetCMulti', st_THINjetCMulti)
    outTree.Branch('st_THINjetNMultiplicity', st_THINjetNMultiplicity)
    outTree.Branch('st_THINjetCorrUnc', st_THINjetCorrUnc)
    outTree.Branch('st_THINbRegNNResolution', st_THINbRegNNResolution)
    outTree.Branch('st_THINbRegNNCorr',  st_THINbRegNNCorr)
    outTree.Branch('st_THINPUjetIDLoose', st_THINPUjetIDLoose)
    outTree.Branch('st_THINPUjetIDMedium', st_THINPUjetIDMedium)
    outTree.Branch('st_THINPUjetIDTight', st_THINPUjetIDTight)
    outTree.Branch('st_THINjetUncSources',st_THINjetUncSources)
    outTree.Branch('st_THINjetUncTotal',st_THINjetUncTotal)

    outTree.Branch('st_TopMatching', st_TopMatching, 'st_TopMatching/L')

    outTree.Branch('st_nfjet', st_nfjet, 'st_nfjet/L')
    outTree.Branch('st_fjetPx', st_fjetPx)
    outTree.Branch('st_fjetPy', st_fjetPy)
    outTree.Branch('st_fjetPz', st_fjetPz)
    outTree.Branch('st_fjetEnergy', st_fjetEnergy)
    outTree.Branch('st_fjetDoubleSV', st_fjetDoubleSV)
    outTree.Branch('st_fjetProbQCDb', st_fjetProbQCDb)
    outTree.Branch('st_fjetProbHbb', st_fjetProbHbb)
    outTree.Branch('st_fjetProbQCDc', st_fjetProbQCDc)
    outTree.Branch('st_fjetProbHcc', st_fjetProbHcc)
    outTree.Branch('st_fjetProbHbbc', st_fjetProbHbbc)
    outTree.Branch('st_fjetProbbbvsLight', st_fjetProbbbvsLight)
    outTree.Branch('st_fjetProbccvsLight', st_fjetProbccvsLight)
    outTree.Branch('st_fjetProbTvsQCD', st_fjetProbTvsQCD)
    outTree.Branch('st_fjetProbWvsQCD', st_fjetProbWvsQCD)
    outTree.Branch('st_fjetProbZHbbvsQCD', st_fjetProbZHbbvsQCD)
    outTree.Branch('st_fjetSDMass', st_fjetSDMass)
    outTree.Branch('st_fjetSDMassCorrFact', st_fjetSDMassCorrFact)
    outTree.Branch('st_fjetN2b1', st_fjetN2b1)
    outTree.Branch('st_fjetN2b2', st_fjetN2b2)
    outTree.Branch('st_fjetTau21', st_fjetTau21)
    outTree.Branch('st_fjetCHSPRMass', st_fjetCHSPRMass)
    outTree.Branch('st_fjetCHSSDMass', st_fjetCHSSDMass)
    outTree.Branch('st_fjetjetUncSources',st_fjetjetUncSources)
    outTree.Branch('st_fjetjetUncTotal',st_fjetjetUncTotal)    

    outTree.Branch('st_nEle', st_nEle, 'st_nEle/L')
    outTree.Branch('st_elePx', st_elePx)
    outTree.Branch('st_elePy', st_elePy)
    outTree.Branch('st_elePz', st_elePz)
    outTree.Branch('st_eleEnergy', st_eleEnergy)
    # , 'st_eleIsPassTight/O' )
    outTree.Branch('st_eleIsPassTight', st_eleIsPassTight)
    # , 'st_eleIsPassLoose/O' )
    outTree.Branch('st_eleIsPassLoose', st_eleIsPassLoose)
    outTree.Branch('st_eleCharge', st_eleCharge)

    outTree.Branch('st_nPho', st_nPho, 'st_nPho/L')
    # , 'st_phoIsPassTight/O' )
    outTree.Branch('st_phoIsPassTight', st_phoIsPassTight)
    outTree.Branch('st_phoPx', st_phoPx)
    outTree.Branch('st_phoPy', st_phoPy)
    outTree.Branch('st_phoPz', st_phoPz)
    outTree.Branch('st_phoEnergy', st_phoEnergy)

    outTree.Branch('st_nMu', st_nMu, 'st_nMu/L')
    outTree.Branch('st_muPx', st_muPx)
    outTree.Branch('st_muPy', st_muPy)
    outTree.Branch('st_muPz', st_muPz)
    outTree.Branch('st_muEnergy', st_muEnergy)
    outTree.Branch('st_isTightMuon', st_isTightMuon)  # , 'st_isTightMuon/O' )
    outTree.Branch('st_muCharge', st_muCharge)
    #outTree.Branch( 'st_muIso', st_muIso)#, 'st_muIso/F')

    #outTree.Branch( 'st_HPSTau_n', st_HPSTau_n, 'st_HPSTau_n/L')
    outTree.Branch('st_nTau_DRBased_EleMuVeto',
                   st_nTau_DRBased_EleMuVeto, 'st_nTau_DRBased_EleMuVeto/L')
    outTree.Branch('st_nTau_discBased_looseElelooseMuVeto',
                   st_nTau_discBased_looseElelooseMuVeto, 'st_nTau_discBased_looseElelooseMuVeto/L')
    outTree.Branch('st_nTau_discBased_looseEleTightMuVeto',
                   st_nTau_discBased_looseEleTightMuVeto, 'st_nTau_discBased_looseEleTightMuVeto/L')
    outTree.Branch('st_nTau_discBased_mediumElelooseMuVeto',
                   st_nTau_discBased_mediumElelooseMuVeto, 'st_nTau_discBased_mediumElelooseMuVeto/L')
    outTree.Branch('st_nTau_discBased_TightElelooseMuVeto',
                   st_nTau_discBased_TightElelooseMuVeto, 'st_nTau_discBased_TightElelooseMuVeto/L')
    outTree.Branch('st_nTau_discBased_TightEleTightMuVeto',
                   st_nTau_discBased_TightEleTightMuVeto, 'st_nTau_discBased_TightEleTightMuVeto/L')

    '''
    outTree.Branch( 'st_Taudisc_againstLooseMuon', st_Taudisc_againstLooseMuon)
    outTree.Branch( 'st_Taudisc_againstTightMuon', st_Taudisc_againstTightMuon)
    outTree.Branch( 'st_Taudisc_againstLooseElectron', st_Taudisc_againstLooseElectron)
    outTree.Branch( 'st_Taudisc_againstMediumElectron', st_Taudisc_againstMediumElectron)

    outTree.Branch( 'st_tau_isoLoose', st_tau_isoLoose)
    outTree.Branch( 'st_tau_isoMedium', st_tau_isoMedium)
    outTree.Branch( 'st_tau_isoTight', st_tau_isoTight)
    outTree.Branch('st_tau_dm',st_tau_dm)
    '''

    outTree.Branch('st_pu_nTrueInt', st_pu_nTrueInt, 'st_pu_nTrueInt/F')
    outTree.Branch('st_pu_nPUVert', st_pu_nPUVert, 'st_pu_nPUVert/F')
    outTree.Branch('st_THINjetNPV', st_THINjetNPV, 'st_THINjetNPV/F')
    outTree.Branch('mcweight', mcweight, 'mcweight/F')
    # outTree.Branch( 'st_nGenPar',st_nGenPar,'st_nGenPar/L' )  #nGenPar/I
    # outTree.Branch( 'st_genParId',st_genParId )  #vector<int>
    # outTree.Branch( 'st_genMomParId',st_genMomParId )
    # outTree.Branch( 'st_genParSt',st_genParSt )
    # outTree.Branch( 'st_genParPx', st_genParPx  )
    # outTree.Branch( 'st_genParPy' , st_genParPy )
    # outTree.Branch( 'st_genParPz', st_genParPz )
    # outTree.Branch( 'st_genParEnergy', st_genParEnergy )
    #outTree.Branch('st_METXYCorr_Met_MetPhi', st_METXYCorr_Met_MetPhi)

    outTree.Branch('st_genParPt', st_genParPt, )
    outTree.Branch('st_genParSample', st_genParSample)

    outTree.Branch('WenuRecoil', WenuRecoil, 'WenuRecoil/F')
    outTree.Branch('Wenumass', Wenumass, 'Wenumass/F')
    outTree.Branch('WenuPhi', WenuPhi, 'WenuPhi/F')

    outTree.Branch('WmunuRecoil', WmunuRecoil, 'WmunuRecoil/F')
    outTree.Branch('Wmunumass', Wmunumass, 'Wmunumass/F')
    outTree.Branch('WmunuPhi', WmunuPhi, 'WmunuPhi/F')

    outTree.Branch('ZeeRecoil', ZeeRecoil, 'ZeeRecoil/F')
    outTree.Branch('ZeeMass', ZeeMass, 'ZeeMass/F')
    outTree.Branch('ZeePhi', ZeePhi, 'ZeePhi/F')

    outTree.Branch('ZmumuRecoil', ZmumuRecoil, 'ZmumuRecoil/F')
    outTree.Branch('ZmumuMass', ZmumuMass, 'ZmumuMass/F')
    outTree.Branch('ZmumuPhi', ZmumuPhi, 'ZmumuPhi/F')
    '''
    outTree.Branch( 'GammaRecoil', GammaRecoil, 'GammaRecoil/F')
    outTree.Branch( 'GammaPhi', GammaPhi, 'GammaPhi/F')
    '''

    # trigger status branches
    outTree.Branch('st_eletrigdecision', st_eletrigdecision,
                   'st_eletrigdecision/O')
    outTree.Branch('st_mutrigdecision', st_mutrigdecision,
                   'st_mutrigdecision/O')
    outTree.Branch('st_mettrigdecision', st_mettrigdecision,
                   'st_mettrigdecision/O')
    outTree.Branch('st_photrigdecision', st_photrigdecision,
                   'st_photrigdecision/O')
    outTree.Branch('st_filterstatus', st_filterstatus, 'st_filterstatus/O')

    ## following can be moved to outputtree.py if we manage to change the name of output root file.

    if runOn2016:
        jetvariables = branches.allvars2016
    elif runOn2017:
        jetvariables = branches.allvars2017
    elif runOn2018:
        jetvariables = branches.allvars2018

    if runOn2017 or runOn2018:
        if monoh_zpb or bbdm_2hdma or bbDM_DMSimp:
            jetvariables.append('mass_A')
            jetvariables.append('mass_a')
    filename = infile_

    h_eventCounter = TH1F('h_eventCounter', 'h_eventCounter', 2, 0.5, 2.5)
    for infl in infile_:
        f_tmp = TFile.Open(infl, 'READ')
        h_tmp = f_tmp.Get('trigFilter/event_counter_')
        h_eventCounter.Add(h_tmp)

    print "now ready to read rootfile as dataframe"
    ieve = 0
    icount = 0
    #print "running on", filename
    for df in read_root(filename, 'tree/treeMaker', columns=jetvariables, chunksize=125000):
        if runOn2016:
            df['mass_A'] = 0
            df['mass_a'] = 0
            var_zip = zip(df.runId, df.lumiSection, df.eventId, df.isData, df.mcWeight, df.mass_A,df.mass_a,
                          df.prefiringweight, df.prefiringweightup, df.prefiringweightdown,
                          df.pu_nTrueInt, df.pu_nPUVert, df.nVtx,
                          df.hlt_trigName, df.hlt_trigResult, df.hlt_filterName, df.hlt_filterResult,df.pdfscaleSysWgtID_,df.pdfscaleSysWeights,
                          df.pfpatMet_smear, df.pfMetCorrPt, df.pfMetCorrPhi, df.pfMetCorrUnc,
                          df.pfMetCorrSig, df.pfpatCaloMETPt, df.pfpatCaloMETPhi, df.pfTRKMETPt_, df.pfTRKMETPhi_, df.pfMetRawPt, df.pfMetRawPhi,
                          df.nEle, df.elePx, df.elePy, df.elePz, df.eleEnergy, df.eleIsPassVeto, df.eleIsPassLoose, df.eleIsPassTight, df.eleD0, df.eleDz,
                          df.eleCharge, df.nPho, df.phoPx, df.phoPy, df.phoPz, df.phoEnergy, df.phoIsPassLoose, df.phoIsPassTight,
                          df.nMu, df.muPx, df.muPy, df.muPz, df.muEnergy, df.isLooseMuon, df.isTightMuon, df.PFIsoLoose, df.PFIsoMedium, df.PFIsoTight, df.PFIsoVeryTight, df.muCharge,
                          df.HPSTau_n, df.HPSTau_Px, df.HPSTau_Py, df.HPSTau_Pz, df.HPSTau_Energy, df.disc_decayModeFinding, df.disc_byLooseIsolationMVArun2017v2DBoldDMwLT2017, df.disc_byMediumIsolationMVArun2017v2DBoldDMwLT2017, df.disc_byTightIsolationMVArun2017v2DBoldDMwLT2017,
                          df.disc_againstMuonLoose3, df.disc_againstMuonTight3, df.disc_againstElectronLooseMVA6, df.disc_againstElectronMediumMVA6, df.disc_againstElectronTightMVA6,
                          df.nGenPar, df.genParId, df.genMomParId, df.genParSt, df.genParPx, df.genParPy, df.genParPz, df.genParE,
                          df.THINnJet, df.THINjetPx, df.THINjetPy, df.THINjetPz, df.THINjetEnergy, df.THINbRegNNResolution, df.THINbRegNNCorr,df.THINisPUJetIDLoose,df.THINisPUJetIDMedium,df.THINisPUJetIDTight,
                          df.THINjetPassIDLoose, df.THINjetDeepCSV_b, df.THINjetHadronFlavor, df.THINjetCEmEF, df.THINjetCHadEF, df.THINjetNEmEF, df.THINjetNHadEF, df.THINjetCMulti, df.THINjetNMultiplicity, df.THINjetCorrUncUp, df.THINjetNPV, df.THINjetUncSources, df.THINjetUncTotal,
                          df.FATnJet, df.FATjetPx, df.FATjetPy, df.FATjetPz, df.FATjetEnergy, df.FATgenjetpx, df.FATgenjetpy, df.FATgenjetpz, df.FATgenjetE, df.FATjetPassIDLoose,
                          df.FATjet_DoubleSV, df.FATjet_probQCDb, df.FATjet_probHbb, df.FATjet_probQCDc, df.FATjet_probHcc, df.FATjet_probHbbc,
                          df.FATjet_prob_bbvsLight, df.FATjet_prob_ccvsLight, df.FATjet_prob_TvsQCD, df.FATjet_prob_WvsQCD, df.FATjet_prob_ZHbbvsQCD,
                          df.FATjetSDmass, df.FATN2_Beta1_, df.FATN2_Beta2_, df.FATjetCHSPRmassL2L3Corr, df.FATjetCHSSDmassL2L3Corr, df.FATjetTau1, df.FATjetTau2, df.FATjetUncSources, df.FATjetUncTotal)
        elif runOn2017:
            if ('mass_A' not in df.columns) and('mass_a' not in df.columns):
                df['mass_A'] = 0
                df['mass_a'] = 0
            var_zip = zip(df.runId, df.lumiSection, df.eventId, df.isData, df.mcWeight, df.mass_A, df.mass_a,
                          df.prefiringweight, df.prefiringweightup, df.prefiringweightdown,
                          df.pu_nTrueInt, df.pu_nPUVert, df.nVtx,
                          df.hlt_trigName, df.hlt_trigResult, df.hlt_filterName, df.hlt_filterResult, df.pdfscaleSysWgtID_, df.pdfscaleSysWeights,
                          df.pfpatmodifiedMet_smear, df.pfmodifiedMetCorrPt, df.pfmodifiedMetCorrPhi, df.pfmodifiedMetCorrUnc,
                          df.pfmodifiedMetCorrSig, df.pfpatCaloMETPt, df.pfpatCaloMETPhi, df.pfTRKMETPt_, df.pfTRKMETPhi_, df.pfMetRawPt, df.pfMetRawPhi,
                          df.nEle, df.elePx, df.elePy, df.elePz, df.eleEnergy, df.eleIsPassVeto, df.eleIsPassLoose, df.eleIsPassTight, df.eleD0, df.eleDz,
                          df.eleCharge, df.nPho, df.phoPx, df.phoPy, df.phoPz, df.phoEnergy, df.phoIsPassLoose, df.phoIsPassTight,
                          df.nMu, df.muPx, df.muPy, df.muPz, df.muEnergy, df.isLooseMuon, df.isTightMuon, df.PFIsoLoose, df.PFIsoMedium, df.PFIsoTight, df.PFIsoVeryTight, df.muCharge,
                          df.HPSTau_n, df.HPSTau_Px, df.HPSTau_Py, df.HPSTau_Pz, df.HPSTau_Energy, df.disc_decayModeFinding, df.disc_byLooseIsolationMVArun2017v2DBoldDMwLT2017, df.disc_byMediumIsolationMVArun2017v2DBoldDMwLT2017, df.disc_byTightIsolationMVArun2017v2DBoldDMwLT2017,
                          df.disc_againstMuonLoose3, df.disc_againstMuonTight3, df.disc_againstElectronLooseMVA6, df.disc_againstElectronMediumMVA6, df.disc_againstElectronTightMVA6,
                          df.nGenPar, df.genParId, df.genMomParId, df.genParSt, df.genParPx, df.genParPy, df.genParPz, df.genParE,
                          df.THINnJet, df.THINjetPx, df.THINjetPy, df.THINjetPz, df.THINjetEnergy, df.THINbRegNNResolution, df.THINbRegNNCorr,df.THINisPUJetIDLoose,df.THINisPUJetIDMedium,df.THINisPUJetIDTight,
                          df.THINjetPassIDTight, df.THINjetDeepCSV_b, df.THINjetHadronFlavor, df.THINjetCEmEF, df.THINjetCHadEF, df.THINjetNEmEF, df.THINjetNHadEF, df.THINjetCMulti, df.THINjetNMultiplicity, df.THINjetCorrUncUp, df.THINjetNPV, df.THINjetUncSources, df.THINjetUncTotal,
                          df.FATnJet, df.FATjetPx, df.FATjetPy, df.FATjetPz, df.FATjetEnergy, df.FATgenjetpx, df.FATgenjetpy, df.FATgenjetpz, df.FATgenjetE, df.FATjetPassIDTight,
                          df.FATjet_DoubleSV, df.FATjet_probQCDb, df.FATjet_probHbb, df.FATjet_probQCDc, df.FATjet_probHcc, df.FATjet_probHbbc,
                          df.FATjet_prob_bbvsLight, df.FATjet_prob_ccvsLight, df.FATjet_prob_TvsQCD, df.FATjet_prob_WvsQCD, df.FATjet_prob_ZHbbvsQCD,
                          df.FATjetSDmass, df.FATN2_Beta1_, df.FATN2_Beta2_, df.FATjetCHSPRmassL2L3Corr, df.FATjetCHSSDmassL2L3Corr, df.FATjetTau1, df.FATjetTau2, df.FATjetUncSources, df.FATjetUncTotal)
        elif runOn2018:
            if ('mass_A' not in df.columns) and('mass_a' not in df.columns):
                df['mass_A'] = 0
                df['mass_a'] = 0
            df['prefiringweight'] = 1.0
            df['prefiringweightup'] = 1.0
            df['prefiringweightdown'] = 1.0
            var_zip = zip(df.runId, df.lumiSection, df.eventId, df.isData, df.mcWeight,df.mass_A,df.mass_a,
                          df.prefiringweight, df.prefiringweightup, df.prefiringweightdown,
                          df.pu_nTrueInt, df.pu_nPUVert, df.nVtx,
                          df.hlt_trigName, df.hlt_trigResult, df.hlt_filterName, df.hlt_filterResult, df.pdfscaleSysWgtID_, df.pdfscaleSysWeights,
                          df.pfpatMet_smear, df.pfMetCorrPt, df.pfMetCorrPhi, df.pfMetCorrUnc,
                          df.pfMetCorrSig, df.pfpatCaloMETPt, df.pfpatCaloMETPhi, df.pfTRKMETPt_, df.pfTRKMETPhi_, df.pfMetRawPt, df.pfMetRawPhi,
                          df.nEle, df.elePx, df.elePy, df.elePz, df.eleEnergy, df.eleIsPassVeto, df.eleIsPassLoose, df.eleIsPassTight, df.eleD0, df.eleDz,
                          df.eleCharge, df.nPho, df.phoPx, df.phoPy, df.phoPz, df.phoEnergy, df.phoIsPassLoose, df.phoIsPassTight,
                          df.nMu, df.muPx, df.muPy, df.muPz, df.muEnergy, df.isLooseMuon, df.isTightMuon, df.PFIsoLoose, df.PFIsoMedium, df.PFIsoTight, df.PFIsoVeryTight, df.muCharge,
                          df.HPSTau_n, df.HPSTau_Px, df.HPSTau_Py, df.HPSTau_Pz, df.HPSTau_Energy, df.disc_decayModeFinding, df.disc_byLooseIsolationMVArun2017v2DBoldDMwLT2017, df.disc_byMediumIsolationMVArun2017v2DBoldDMwLT2017, df.disc_byTightIsolationMVArun2017v2DBoldDMwLT2017,
                          df.disc_againstMuonLoose3, df.disc_againstMuonTight3, df.disc_againstElectronLooseMVA6, df.disc_againstElectronMediumMVA6, df.disc_againstElectronTightMVA6,
                          df.nGenPar, df.genParId, df.genMomParId, df.genParSt, df.genParPx, df.genParPy, df.genParPz, df.genParE,
                          df.THINnJet, df.THINjetPx, df.THINjetPy, df.THINjetPz, df.THINjetEnergy, df.THINbRegNNResolution, df.THINbRegNNCorr,df.THINisPUJetIDLoose,df.THINisPUJetIDMedium,df.THINisPUJetIDTight,
                          df.THINjetPassIDTight, df.THINjetDeepCSV_b, df.THINjetHadronFlavor, df.THINjetCEmEF, df.THINjetCHadEF, df.THINjetNEmEF, df.THINjetNHadEF, df.THINjetCMulti, df.THINjetNMultiplicity, df.THINjetCorrUncUp, df.THINjetNPV, df.THINjetUncSources, df.THINjetUncTotal,
                          df.FATnJet, df.FATjetPx, df.FATjetPy, df.FATjetPz, df.FATjetEnergy, df.FATgenjetpx, df.FATgenjetpy, df.FATgenjetpz, df.FATgenjetE, df.FATjetPassIDTight,
                          df.FATjet_DoubleSV, df.FATjet_probQCDb, df.FATjet_probHbb, df.FATjet_probQCDc, df.FATjet_probHcc, df.FATjet_probHbbc,
                          df.FATjet_prob_bbvsLight, df.FATjet_prob_ccvsLight, df.FATjet_prob_TvsQCD, df.FATjet_prob_WvsQCD, df.FATjet_prob_ZHbbvsQCD,
                          df.FATjetSDmass, df.FATN2_Beta1_, df.FATN2_Beta2_, df.FATjetCHSPRmassL2L3Corr, df.FATjetCHSSDmassL2L3Corr, df.FATjetTau1, df.FATjetTau2, df.FATjetUncSources, df.FATjetUncTotal)
        for run, lumi, event, isData, mcWeight_, mass_A_, mass_a_,\
                prefiringweight_, prefiringweightup_, prefiringweightdown_,\
                pu_nTrueInt_, pu_nPUVert_,nVtx,\
                trigName_, trigResult_, filterName, filterResult, pdfscaleSysWgtID, pdfscaleSysWeights,\
                met_smear, type1met_, type1metphi_, metUnc_,\
                metCorrSig, patCaloMETPt, patCaloMETPhi, TRKMETPt_, TRKMETPhi_, MetRawPt, MetRawPhi,\
                nele_, elepx_, elepy_, elepz_, elee_, elevetoid_, elelooseid_, eletightid_, eleD0_, eleDz_,\
                eleCharge_, npho_, phopx_, phopy_, phopz_, phoe_, pholooseid_, photightID_,\
                nmu_, mupx_, mupy_, mupz_, mue_, mulooseid_, mutightid_, muisoloose, muisomedium, muisotight, muisovtight, muCharge_,\
                nTau_, tau_px_, tau_py_, tau_pz_, tau_e_, tau_dm_, tau_isLoose_, tau_isoMedium_, tau_isoTight_,\
                Taudisc_againstLooseMuon, Taudisc_againstTightMuon, Taudisc_againstLooseElectron, Taudisc_againstMediumElectron, Taudisc_againstTightElectron,\
                nGenPar_, genParId_, genMomParId_, genParSt_, genpx_, genpy_, genpz_, gene_,\
                nak4jet_, ak4px_, ak4py_, ak4pz_, ak4e_, ak4bRegNNResolution, ak4bRegNNCorr,ak4PUJetIDLoose,ak4PUJetIDMedium,ak4PUJetIDTight,\
                ak4PassID_, ak4deepcsv_, ak4flavor_, ak4CEmEF_, ak4CHadEF_, ak4NEmEF_, ak4NHadEF_, ak4CMulti_, ak4NMultiplicity_, ak4JEC_, ak4NPV_, ak4jetUncSources, ak4jetUncTotal,\
                fatnJet, fatjetPx, fatjetPy, fatjetPz, fatjetEnergy, fatgenjetPx, fatgenjetPy, fatgenjetPz, fatgenjetEnergy, fatjetPassID,\
                fatjet_DoubleSV, fatjet_probQCDb, fatjet_probHbb, fatjet_probQCDc, fatjet_probHcc, fatjet_probHbbc,\
                fatjet_prob_bbvsLight, fatjet_prob_ccvsLight, fatjet_prob_TvsQCD, fatjet_prob_WvsQCD, fatjet_prob_ZHbbvsQCD,\
                fatjetSDmass, fatN2_Beta1_, fatN2_Beta2_, fatjetCHSPRmassL2L3Corr, fatjetCHSSDmassL2L3Corr, fatjetTau1, fatjetTau2, fatjetUncSources, fatjetUncTotal\
                in var_zip:
            if debug_:
                print len(trigName_), len(trigResult_), len(filterName), len(filterResult), len(metUnc_), len(elepx_), len(elepy_), len(elepz_), len(elee_), len(elevetoid_), len(elelooseid_), len(eletightid_), len(eleCharge_), npho_, len(phopx_), len(phopy_), len(phopz_), len(phoe_), len(pholooseid_), len(photightID_), nmu_, len(mupx_), len(mupy_), len(mupz_), len(mue_), len(mulooseid_), len(mutightid_), len(muisoloose), len(muisomedium), len(muisotight), len(muisovtight), len(muCharge_), nTau_, len(tau_px_), len(tau_py_), len(tau_pz_), len(tau_e_), len(tau_dm_), len(tau_isLoose_), len(genParId_), len(genMomParId_), len(genParSt_), len(genpx_), len(genpy_), len(genpz_), len(gene_), len(ak4px_), len(ak4py_), len(ak4pz_), len(ak4e_), len(ak4PassID_), len(ak4deepcsv_), len(ak4flavor_), len(ak4CEmEF_), len(ak4CHadEF_), len(ak4NEmEF_), len(ak4NHadEF_), len(ak4CMulti_), len(ak4NMultiplicity_), len(ak4JEC_), len(fatjetPx), len(fatjetPy), len(fatjetPz), len(fatjetEnergy), len(fatjetPassID), len(fatjet_DoubleSV), len(fatjet_probQCDb), len(fatjet_probHbb), len(fatjet_probQCDc), len(fatjet_probHcc), len(fatjet_probHbbc), len(fatjet_prob_bbvsLight), len(fatjet_prob_ccvsLight), len(fatjet_prob_TvsQCD), len(fatjet_prob_WvsQCD), len(fatjet_prob_ZHbbvsQCD), len(fatjetSDmass), len(fatN2_Beta1_), len(fatN2_Beta2_), len(fatjetCHSPRmassL2L3Corr), len(fatjetCHSSDmassL2L3Corr)
            if (monoh_zpb or bbDM_DMSimp or bbdm_2hdma):
		if (int(mass_A_) != int(mA_)) or (int(mass_a_) != int(ma_)): continue
            if ieve % 1000 == 0:
                print "Processed", ieve, "Events"
            ieve = ieve + 1
            # -------------------------------------------------
            # MC Weights
            # -------------------------------------------------
            mcweight[0] = 0.0
            if isData == 1:
                mcweight[0] = 1.0
            if not isData:
                if mcWeight_ < 0:
                    mcweight[0] = -1.0
                if mcWeight_ > 0:
                    mcweight[0] = 1.0
            h_total.Fill(1.)
            h_total_mcweight.Fill(1., mcweight[0])

            # -------------------------------------------------
            ## Trigger selection
            # -------------------------------------------------

            eletrigdecision = False
            mudecision = False
            metdecision = False
            phodecision = False

            eletrigstatus = [(anautil.CheckFilter(
                trigName_, trigResult_, eletrig[itrig])) for itrig in range(len(eletrig))]
            mutrigstatus = [(anautil.CheckFilter(
                trigName_, trigResult_, muontrig[itrig])) for itrig in range(len(muontrig))]
            mettrigstatus = [(anautil.CheckFilter(
                trigName_, trigResult_, mettrig[itrig])) for itrig in range(len(mettrig))]
            photrigstatus = [(anautil.CheckFilter(
                trigName_, trigResult_, photontrig[itrig])) for itrig in range(len(photontrig))]

            eletrigdecision = boolutil.logical_OR(eletrigstatus)
            mutrigdecision = boolutil.logical_OR(mutrigstatus)
            mettrigdecision = boolutil.logical_OR(mettrigstatus)
            photrigdecision = boolutil.logical_OR(photrigstatus)
            '''
            if not isData:
                eletrigdecision = True
                mutrigdecision = True
                mettrigdecision = True
                photrigdecision = True
            '''

            # ------------------------------------------------------
            ## Filter selection
            # ------------------------------------------------------
            filterdecision = False
            filterstatus = [False for ifilter in range(len(filter_list))]
            filterstatus = [anautil.CheckFilter(
                filterName, filterResult, filter_list[ifilter]) for ifilter in range(len(filter_list))]

            '''
            if not isData:     filterdecision = True
            if isData:         filterdecision  = boolutil.logical_AND(filterstatus)
            '''
            filterdecision = boolutil.logical_AND(filterstatus)
            if filterdecision == False and isData:
                continue

	    # MET xy-shift corrections
            METXYCorr_Met_MetPhi = ROOT.METXYCorr_Met_MetPhi(type1met_, type1metphi_,int(run),int(args.year), not isData,int(nVtx))
	    met_    = METXYCorr_Met_MetPhi[0]
	    metphi_ = METXYCorr_Met_MetPhi[1]
            # ------------------------------------------------------
            ## PFMET Selection
            # --------------------------------------------------------
            pfmetstatus = (met_ > 180.0) or (met_smear > 180.0)



            '''
            ****   *      ****
            *      *      *
            ***    *      ***
            *      *      *
            ****   ****   ****
            '''

            ''' removing for loop
            elept = [getPt(elepx_[ie], elepy_[ie]) for ie in range(nele_)]
            eleeta = [getEta(elepx_[ie], elepy_[ie], elepz_[ie]) for ie in range(nele_)]
            elephi = [getPhi(elepx_[ie], elepy_[ie]) for ie in range(nele_)]
            ele_pt10_eta2p5_vetoID   = [(elept[ie] > 10.0) and (elevetoid_[ie])  and (((abs(eleeta[ie]) > 1.566 or abs(eleeta[ie]) < 1.4442) and (abs(eleeta[ie]) < 2.5))) for ie in range(nele_)]
            ele_pt10_eta2p5_looseID  = [(elept[ie] > 10.0) and (elelooseid_[ie]) and (((abs(eleeta[ie]) > 1.566 or abs(eleeta[ie]) < 1.4442) and (abs(eleeta[ie]) < 2.5))) for ie in range(nele_)]
            ele_pt30_eta2p5_tightID  = [(elept[ie] > 30.0) and (eletightid_[ie]) and (((abs(eleeta[ie]) > 1.566 or abs(eleeta[ie]) < 1.4442) and (abs(eleeta[ie]) < 2.5))) for ie in range(nele_)]
            '''

            elept = getPt(elepx_, elepy_)
            eleeta = getEta(elepx_, elepy_, elepz_)
            elephi = getPhi(elepx_, elepy_)

            ele_pt10_eta2p5_vetoID = boolutil.logical_and3((elept > 10.0), (elevetoid_),  numpy.logical_and(
                numpy.logical_or(numpy.abs(eleeta) > 1.566, numpy.abs(eleeta) < 1.4442), (numpy.abs(eleeta) < 2.5)))

            ele_pt10_eta2p5_looseID = boolutil.logical_and3((elept > 10.0), (elelooseid_),  numpy.logical_and(
                numpy.logical_or(numpy.abs(eleeta) > 1.566, numpy.abs(eleeta) < 1.4442), (numpy.abs(eleeta) < 2.5)))

            ele_pt30_eta2p5_tightID = boolutil.logical_and3((elept > 30.0), (eletightid_),  numpy.logical_and(numpy.logical_or(boolutil.logical_and3(numpy.abs(eleeta) > 1.566, numpy.abs(
                eleD0_) < 0.10, numpy.abs(eleDz_) < 0.20), boolutil.logical_and3(numpy.abs(eleeta) < 1.4442, numpy.abs(eleD0_) < 0.05, numpy.abs(eleDz_) < 0.10)), (numpy.abs(eleeta) < 2.5)))

            pass_ele_veto_index = boolutil.WhereIsTrue(ele_pt10_eta2p5_vetoID)
            pass_ele_loose_index = boolutil.WhereIsTrue(
                ele_pt10_eta2p5_looseID)

            '''
            **     *  *     *
            * *  * *  *     *
            *  *   *  *     *
            *      *  *     *
            *      *   *****
            '''
            mupt = getPt(mupx_, mupy_)
            mueta = getEta(mupx_, mupy_, mupz_)
            muphi = getPhi(mupx_, mupy_)
            mu_pt10_eta2p4_looseID_looseISO = boolutil.logical_and4(
                mupt > 10.0, numpy.abs(mueta) < 2.4,  mulooseid_, muisoloose)
            mu_pt30_eta2p4_tightID_tightISO = boolutil.logical_and4(
                (mupt > 30.0), (numpy.abs(mueta) < 2.4), (mutightid_), (muisotight))

            pass_mu_index = boolutil.WhereIsTrue(
                mu_pt10_eta2p4_looseID_looseISO)

            '''
            *******   *      *   ******
            *     *   *      *  *      *
            *******   ********  *      *
            *         *      *  *      *
            *         *      *   ******
            '''

            #phopt = [getPt(phopx_[ip], phopy_[ip]) for ip in range(npho_)]
            #phoeta = [getEta(phopx_[ip], phopy_[ip], phopz_[ip]) for ip in range(npho_)]
            #pho_pt15_eta2p5_looseID = [ (phopt[ip] > 15.0) and (abs(phoeta[ip]) < 2.5) and (pholooseid_[ip])               for ip in range(npho_)]
            #pass_pho_index = boolutil.WhereIsTrue(pho_pt15_eta2p5_looseID)

            phopt = getPt(phopx_, phopy_)
            phoeta = getEta(phopx_, phopy_, phopz_)
            phophi = getPhi(phopx_, phopy_)

            pho_pt15_eta2p5_looseID = boolutil.logical_and3(
                (phopt > 15.0),   (numpy.abs(phoeta) < 2.5),  (pholooseid_))
            pass_pho_index = boolutil.WhereIsTrue(pho_pt15_eta2p5_looseID)

            cleanedPho_ag_ele = []; cleanedPho_ag_mu = [];pass_pho_index_cleaned=[]
            if npho_ > 0: #and ep_nEle > 0:
                cleanedPho_ag_ele = anautil.jetcleaning(pho_pt15_eta2p5_looseID, ele_pt10_eta2p5_looseID, phoeta, eleeta, phophi, elephi, 0.4)
                cleanedPho_ag_mu  = anautil.jetcleaning(pho_pt15_eta2p5_looseID, mu_pt10_eta2p4_looseID_looseISO, phoeta, mueta, phophi, muphi, 0.4)
                cleanedPhoton     = boolutil.logical_AND_List2(cleanedPho_ag_ele,cleanedPho_ag_mu)
                pass_pho_index_cleaned = boolutil.WhereIsTrue(cleanedPhoton)

            ## Fill variables for the CRs which require lepton.
            WenuRecoil[0] = -1
            WenuRecoilSmearPt = -1
            Wenumass[0] = -1
            WenuPhi[0] = -10

            WmunuRecoil[0] = -1
            WmunuRecoilSmearPt = -1
            Wmunumass[0] = -1
            WmunuPhi[0] = -10

            ZeeRecoil[0] = -1
            ZeeRecoilSmear = -1
            ZeeMass[0] = -1
            ZeePhi[0] = -10

            ZmumuRecoil[0] = -1
            ZmumuRecoilSmear = -1
            ZmumuMass[0] = -1
            ZmumuPhi[0] = -10

            GammaRecoil[0] = -1
            GammaRecoilSmearPt = -1
            GammaPhi[0] = -10
            if debug_:
                print 'Reached Fill variables'

            # ------------------
            # Z CR
            # ------------------
            ## for dielectron
            if len(pass_ele_loose_index) == 2:
                iele1 = pass_ele_loose_index[0]
                iele2 = pass_ele_loose_index[1]
                if eleCharge_[iele1]*eleCharge_[iele2] < 0:
                    ee_mass = InvMass(elepx_[iele1], elepy_[iele1], elepz_[iele1], elee_[
                                      iele1], elepx_[iele2], elepy_[iele2], elepz_[iele2], elee_[iele2])
                    zeeRecoilPx = -(met_*math.cos(metphi_) +
                                    elepx_[iele1] + elepx_[iele2])
                    zeeRecoilPy = -(met_*math.sin(metphi_) +
                                    elepy_[iele1] + elepy_[iele2])
                    ZeeRecoilPt = math.sqrt(zeeRecoilPx**2 + zeeRecoilPy**2)
                    if ee_mass > 60.0 and ee_mass < 120.0 and ZeeRecoilPt > 180.0:
                        ZeeRecoil[0] = ZeeRecoilPt
                        ZeeMass[0] = ee_mass
                        ZeePhi[0] = mathutil.ep_arctan(
                            zeeRecoilPx, zeeRecoilPy)
                    zeeRecoilSmearPx = - \
                        (met_*math.cos(metphi_) +
                         elepx_[iele1] + elepx_[iele2])
                    zeeRecoilSmearPy = - \
                        (met_*math.sin(metphi_) +
                         elepy_[iele1] + elepy_[iele2])
                    ZeeRecoilSmearPt = math.sqrt(
                        zeeRecoilSmearPx**2 + zeeRecoilSmearPy**2)
                    if ee_mass > 60.0 and ee_mass < 120.0 and ZeeRecoilSmearPt > 180.0:
                        ZeeRecoilSmear = ZeeRecoilSmearPt
            ## for dimu
            if len(pass_mu_index) == 2:
                imu1 = pass_mu_index[0]
                imu2 = pass_mu_index[1]
                if muCharge_[imu1]*muCharge_[imu2] < 0:
                    mumu_mass = InvMass(mupx_[imu1], mupy_[imu1], mupz_[imu1], mue_[
                                        imu1], mupx_[imu2], mupy_[imu2], mupz_[imu2], mue_[imu2])
                    zmumuRecoilPx = -(met_*math.cos(metphi_) +
                                      mupx_[imu1] + mupx_[imu2])
                    zmumuRecoilPy = -(met_*math.sin(metphi_) +
                                      mupy_[imu1] + mupy_[imu2])
                    ZmumuRecoilPt = math.sqrt(
                        zmumuRecoilPx**2 + zmumuRecoilPy**2)
                    if mumu_mass > 60.0 and mumu_mass < 120.0 and ZmumuRecoilPt > 180.0:
                        ZmumuRecoil[0] = ZmumuRecoilPt
                        ZmumuMass[0] = mumu_mass
                        ZmumuPhi[0] = mathutil.ep_arctan(
                            zmumuRecoilPx, zmumuRecoilPy)
                    zmumuRecoilSmearPx = - \
                        (met_*math.cos(metphi_) +
                         mupx_[imu1] + mupx_[imu2])
                    zmumuRecoilSmearPy = - \
                        (met_*math.sin(metphi_) +
                         mupy_[imu1] + mupy_[imu2])
                    ZmumuRecoilSmearPt = math.sqrt(
                        zmumuRecoilSmearPx**2 + zmumuRecoilSmearPy**2)
                    if mumu_mass > 60.0 and mumu_mass < 120.0 and ZmumuRecoilSmearPt > 180.0:
                        ZmumuRecoilSmear = ZmumuRecoilSmearPt
            if len(pass_ele_loose_index) == 2:
                ZRecoilstatus = (ZeeRecoil[0] > 180.0) or (
                    ZeeRecoilSmear > 180.0)
            elif len(pass_mu_index) == 2:
                ZRecoilstatus = (ZmumuRecoil[0] > 180.0) or (
                    ZmumuRecoilSmear > 180.0)
            else:
                ZRecoilstatus = False
            if debug_:
                print 'Reached Z CR'

            # ------------------
            # W CR
            # ------------------
            ## for Single electron
            if len(pass_ele_loose_index) == 1:
                ele1 = pass_ele_loose_index[0]
                # transverse mass defined as sqrt{2pT*MET*(1-cos(dphi)}
                e_mass = MT(elept[ele1], met_, DeltaPhi(elephi[ele1], metphi_))
                WenuRecoilPx = -(met_*math.cos(metphi_) + elepx_[ele1])
                WenuRecoilPy = -(met_*math.sin(metphi_) + elepy_[ele1])
                WenuRecoilPt = math.sqrt(WenuRecoilPx**2 + WenuRecoilPy**2)
                if WenuRecoilPt > 180.0:
                   WenuRecoil[0] = WenuRecoilPt
                   Wenumass[0] = e_mass
                   WenuPhi[0] = mathutil.ep_arctan(WenuRecoilPx, WenuRecoilPy)
                WenuRecoilSmearPx = - \
                    (met_*math.cos(metphi_) + elepx_[ele1])
                WenuRecoilSmearPy = - \
                    (met_*math.sin(metphi_) + elepy_[ele1])
                WenuRecoilSmearPt = math.sqrt(
                    WenuRecoilSmearPx**2 + WenuRecoilSmearPy**2)

            ## for Single muon
            if len(pass_mu_index) == 1:
                mu1 = pass_mu_index[0]
                # transverse mass defined as sqrt{2pT*MET*(1-cos(dphi)}
                mu_mass = MT(mupt[mu1], met_, DeltaPhi(muphi[mu1], metphi_))
                WmunuRecoilPx = -(met_*math.cos(metphi_) + mupx_[mu1])
                WmunuRecoilPy = -(met_*math.sin(metphi_) + mupy_[mu1])
                WmunuRecoilPt = math.sqrt(WmunuRecoilPx**2 + WmunuRecoilPy**2)
                if WmunuRecoilPt > 180.0:
                   WmunuRecoil[0] = WmunuRecoilPt
                   Wmunumass[0] = mu_mass
                   WmunuPhi[0] = mathutil.ep_arctan(
                       WmunuRecoilPx, WmunuRecoilPy)
                WmunuRecoilSmearPx = - \
                    (met_*math.cos(metphi_) + mupx_[mu1])
                WmunuRecoilSmearPy = - \
                    (met_*math.sin(metphi_) + mupy_[mu1])
                WmunuRecoilSmearPt = math.sqrt(
                    WmunuRecoilSmearPx**2 + WmunuRecoilSmearPy**2)

            if len(pass_ele_loose_index) == 1:
                WRecoilstatus = (WenuRecoil[0] > 180.0) or (
                    WenuRecoilSmearPt > 180.0)
            elif len(pass_mu_index) == 1:
                WRecoilstatus = (WmunuRecoil[0] > 180.0) or (
                    WmunuRecoilSmearPt > 180.0)
            else:
                WRecoilstatus = False
            if debug_:
                print 'Reached W CR'

            # ------------------
            # Gamma CR
            # ------------------
            ## for Single photon
            if len(pass_pho_index) >= 1:
                pho1 = pass_pho_index[0]
                GammaRecoilPx = -(met_*math.cos(metphi_) + phopx_[pho1])
                GammaRecoilPy = -(met_*math.sin(metphi_) + phopy_[pho1])
                GammaRecoilPt = math.sqrt(GammaRecoilPx**2 + GammaRecoilPy**2)
                if GammaRecoilPt > 180.0:
                    GammaRecoil[0] = GammaRecoilPt
                    GammaPhi[0] = mathutil.ep_arctan(
                        GammaRecoilPx, GammaRecoilPy)
                GammaRecoilSmearPx = - \
                    (met_*math.cos(metphi_) + phopx_[pho1])
                GammaRecoilSmearPy = - \
                    (met_*math.sin(metphi_) + phopy_[pho1])
                GammaRecoilSmearPt = math.sqrt(
                    GammaRecoilSmearPx**2 + GammaRecoilSmearPy**2)

            GammaRecoilStatus = (GammaRecoil[0] > 180.0) or (
                GammaRecoilSmearPt > 180.0)
            if debug_:
                print 'Reached Gamma CR'

            if pfmetstatus == False and ZRecoilstatus == False and WRecoilstatus == False and GammaRecoilStatus == False:
                continue

            '''
            *******   *****   *******
               *      *          *
               *      ****       *
               *      *          *
            ***       *****      *
            '''

            '''
            ak4pt = [getPt(ak4px_[ij], ak4py_[ij]) for ij in range(nak4jet_)]
            ak4eta = [getEta(ak4px_[ij], ak4py_[ij], ak4pz_[ij]) for ij in range(nak4jet_)]
            ak4phi = [getPhi(ak4px_[ij], ak4py_[ij]) for ij in range(nak4jet_)]
            '''
            ak4pt = getPt(ak4px_, ak4py_)
            ak4eta = getEta(ak4px_, ak4py_, ak4pz_)
            ak4phi = getPhi(ak4px_, ak4py_)
            if runOn2016:
                #ak4PassID_Calc = [jetID_(ak4CEmEF_[ij],ak4CHadEF_[ij],ak4NEmEF_[ij],ak4NHadEF_[ij],ak4CMulti_[ij],ak4NMultiplicity_[ij],ak4eta[ij])[0] for ij in range(nak4jet_)]
                ak4PassID_Calc = ak4PassID_
            if runOn2017:
                #ak4PassID_Calc = [jetID_(ak4CEmEF_[ij],ak4CHadEF_[ij],ak4NEmEF_[ij],ak4NHadEF_[ij],ak4CMulti_[ij],ak4NMultiplicity_[ij],ak4eta[ij])[1] for ij in range(nak4jet_)]
                ak4PassID_Calc = ak4PassID_
            if runOn2018:
                #ak4PassID_Calc = [jetID_(ak4CEmEF_[ij],ak4CHadEF_[ij],ak4NEmEF_[ij],ak4NHadEF_[ij],ak4CMulti_[ij],ak4NMultiplicity_[ij],ak4eta[ij])[1] for ij in range(nak4jet_)]
                ak4PassID_Calc = ak4PassID_

            #ak4_pt30_eta4p5_IDT  =  ( (ak4pt[ij] > 30.0) and (abs(ak4eta[ij]) < 4.5) and (ak4PassID_Calc[ij] ) ) for ij in range(nak4jet_)]
            ak4_pt30_eta4p5_IDT = boolutil.logical_and3(
                (ak4pt > 30.0), (numpy.abs(ak4eta) < 4.5), (ak4PassID_Calc))

            ##--- jet cleaning
            jetCleanAgainstEle = []
            jetCleanAgainstMu = []
            pass_jet_index_cleaned = []

            if len(ak4_pt30_eta4p5_IDT) > 0:
                DRCut = 0.4
                jetCleanAgainstEle = anautil.jetcleaning(
                    ak4_pt30_eta4p5_IDT, ele_pt10_eta2p5_vetoID, ak4eta, eleeta, ak4phi, elephi, DRCut)
                jetCleanAgainstMu = anautil.jetcleaning(
                    ak4_pt30_eta4p5_IDT, mu_pt10_eta2p4_looseID_looseISO, ak4eta, mueta, ak4phi, muphi, DRCut)
                jetCleaned = boolutil.logical_AND_List3(
                    ak4_pt30_eta4p5_IDT, jetCleanAgainstEle, jetCleanAgainstMu)
                pass_jet_index_cleaned = boolutil.WhereIsTrue(jetCleaned)
                if debug_:
                    print "pass_jet_index_cleaned = ", pass_jet_index_cleaned, "nJets= ", len(ak4px_)




            '''
            ******      *******   *****   *******
            *              *      *          *
            *****  ----    *      ****       *
            *              *      *          *
            *           ***       *****      *

            '''
            '''
            fatjetpt = [getPt(fatjetPx[ij], fatjetPy[ij]) for ij in range(fatnJet)]
            fatjeteta = [getEta(fatjetPx[ij], fatjetPy[ij], fatjetPz[ij]) for ij in range(fatnJet)]
            fatjetphi = [getPhi(fatjetPx[ij], fatjetPy[ij]) for ij in range(fatnJet)]

            fatjet_pt200_eta2p5_IDT  = [ ( (fatjetpt[ij] > 200.0) and (abs(fatjeteta[ij]) < 2.5) and (fatjetPassID[ij] ) ) for ij in range(fatnJet)]
            '''

            fatjetpt = getPt(fatjetPx, fatjetPy)
            fatjeteta = getEta(fatjetPx, fatjetPy, fatjetPz)
            fatjetphi = getPhi(fatjetPx, fatjetPy)

            fatgenjetpt = getPt(fatgenjetPx, fatgenjetPy)
            fatgenjeteta = getEta(fatgenjetPx, fatgenjetPy, fatgenjetPz)
            fatgenjetphi = getPhi(fatgenjetPx, fatgenjetPy)

            # if fatnJet==len(fatgenjetpt) and not isData:
            SDMassCorrFact = [TheaCorrection(fatjetpt[ij],fatjeteta[ij]) for ij in range(fatnJet)]
            # else:
            #     SDMassCorrFact = [1.0 for ij in range(fatnJet)]
	          #print 'fatnJet',fatnJet,'SDMassCorrFact',SDMassCorrFact
            fatjet_pt200_eta2p5_IDT = boolutil.logical_and3(
                (fatjetpt > 200.0), (numpy.abs(fatjeteta) < 2.5), (fatjetPassID))

            ##--- fat jet cleaning
            fatjetCleanAgainstEle = []
            fatjetCleanAgainstMu = []
            pass_fatjet_index_cleaned = []

            if len(fatjet_pt200_eta2p5_IDT) > 0:
                fatjetCleanAgainstEle = anautil.jetcleaning(
                    fatjet_pt200_eta2p5_IDT, ele_pt10_eta2p5_vetoID, fatjeteta, eleeta, fatjetphi, elephi, 0.8)
                fatjetCleanAgainstMu = anautil.jetcleaning(
                    fatjet_pt200_eta2p5_IDT, mu_pt10_eta2p4_looseID_looseISO, fatjeteta, mueta, fatjetphi, muphi, 0.8)
                fatjetCleaned = boolutil.logical_AND_List3(
                    fatjet_pt200_eta2p5_IDT, fatjetCleanAgainstEle, fatjetCleanAgainstMu)
                pass_fatjet_index_cleaned = boolutil.WhereIsTrue(fatjetCleaned)
                if debug_:
                    print "pass_fatjet_index_cleaned = ", pass_fatjet_index_cleaned, " nJets =   ", len(fatjetpx)

            isak4JetBasedHemEvent=False;isak8JetBasedHemEvent=False;ismetphiBasedHemEvent1=False;ismetphiBasedHemEvent2=False
            if (runOn2018) and (not isData or 'Run2018D' in outfilename or 'Run2018C' in outfilename):
                isak4JetBasedHemEvent = numpy.logical_and(numpy.logical_and(
                    ak4eta > (-3.0), ak4eta < (-1.3)), numpy.logical_and(ak4phi > (-1.57), ak4phi < (-0.87))).any()
                isak8JetBasedHemEvent = numpy.logical_and(numpy.logical_and(
                    fatjeteta > (-3.0), fatjeteta < (-1.3)), numpy.logical_and(fatjetphi > (-1.57), fatjetphi < (-0.87))).any()
                ismetphiBasedHemEvent1 = metphi_ < -0.65 and metphi_ > -1.65 and met_ < 470
                ismetphiBasedHemEvent2 = metphi_ < -0.65 and metphi_ > -1.65


            '''
            ********    *        *       *
               *      *    *     *       *
               *     *      *    *       *
               *     ********    *       *
               *     *      *    *       *
               *     *      *     *******
            '''
            taupt = getPt(tau_px_, tau_py_)
            taueta = getEta(tau_px_, tau_py_, tau_pz_)
            tauphi = getPhi(tau_px_, tau_py_)

            tau_eta2p3_iDLdm_pt18 = boolutil.logical_AND_List4(
                (taupt > 18.0), (numpy.abs(taueta) < 2.3), (tau_isLoose_), (tau_dm_))

            if debug_:
                print "tau_eta2p3_iDLdm_pt18 = ", tau_eta2p3_iDLdm_pt18

            '''
            tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto  = [ ( (taupt[itau] > 18.0) and (abs(taueta[itau]) < 2.3) and (tau_isLoose_[itau]) and (tau_dm_[itau]) and (Taudisc_againstLooseElectron[itau]) and (Taudisc_againstLooseMuon[itau]) ) for itau in range(nTau_)]
            tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto  = [ ( (taupt[itau] > 18.0) and (abs(taueta[itau]) < 2.3) and (tau_isLoose_[itau]) and (tau_dm_[itau]) and (Taudisc_againstLooseElectron[itau]) and (Taudisc_againstTightMuon[itau]) ) for itau in range(nTau_)]
            tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto = [ ( (taupt[itau] > 18.0) and (abs(taueta[itau]) < 2.3) and (tau_isLoose_[itau]) and (tau_dm_[itau]) and (Taudisc_againstMediumElectron[itau]) and (Taudisc_againstLooseMuon[itau])) for itau in range(nTau_)]
            tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto  = [ ( (taupt[itau] > 18.0) and (abs(taueta[itau]) < 2.3) and (tau_isLoose_[itau]) and (tau_dm_[itau]) and (Taudisc_againstTightElectron[itau]) and (Taudisc_againstLooseMuon[itau])) for itau in range(nTau_)]
            tau_eta2p3_iDLdm_pt18_tightEleVeto_tightMuVeto  = [ ( (taupt[itau] > 18.0) and (abs(taueta[itau]) < 2.3) and (tau_isLoose_[itau]) and (tau_dm_[itau]) and (Taudisc_againstTightElectron[itau]) and (Taudisc_againstTightMuon[itau])) for itau in range(nTau_)]
            '''
            tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto = boolutil.logical_and6((taupt > 18.0), (numpy.abs(
                taueta) < 2.3), (tau_isLoose_), (tau_dm_), (Taudisc_againstLooseElectron), (Taudisc_againstLooseMuon))
            tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto = boolutil.logical_and6((taupt > 18.0), (numpy.abs(
                taueta) < 2.3), (tau_isLoose_), (tau_dm_), (Taudisc_againstLooseElectron), (Taudisc_againstTightMuon))
            tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto = boolutil.logical_and6((taupt > 18.0), (numpy.abs(
                taueta) < 2.3), (tau_isLoose_), (tau_dm_), (Taudisc_againstMediumElectron), (Taudisc_againstLooseMuon))
            tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto = boolutil.logical_and6((taupt > 18.0), (numpy.abs(
                taueta) < 2.3), (tau_isLoose_), (tau_dm_), (Taudisc_againstTightElectron), (Taudisc_againstLooseMuon))
            tau_eta2p3_iDLdm_pt18_tightEleVeto_tightMuVeto = boolutil.logical_and6((taupt > 18.0), (numpy.abs(
                taueta) < 2.3), (tau_isLoose_), (tau_dm_), (Taudisc_againstTightElectron), (Taudisc_againstTightMuon))

            tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto_index = boolutil.WhereIsTrue(
                tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto)
            tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto_index = boolutil.WhereIsTrue(
                tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto)
            tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto_index = boolutil.WhereIsTrue(
                tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto)
            tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto_index = boolutil.WhereIsTrue(
                tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto)
            tau_eta2p3_iDLdm_pt18_tightEleVeto_tightMuVeto_index = boolutil.WhereIsTrue(
                tau_eta2p3_iDLdm_pt18_tightEleVeto_tightMuVeto)
            '''
            print 'tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto_index', tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto_index, 'tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto', tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto
            print 'tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto_index', tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto_index, 'tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto',tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto
            print 'tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto_index',tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto_index,'tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto',tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto
            print 'tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto_index',tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto_index,'tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto',tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto
            '''
            tauCleanAgainstEle = []
            tauCleanAgainstMu = []
            pass_tau_index_cleaned_DRBased = []
            if len(tau_eta2p3_iDLdm_pt18) > 0:
                DRCut = 0.4
                tauCleanAgainstEle = anautil.jetcleaning(
                    tau_eta2p3_iDLdm_pt18, ele_pt10_eta2p5_looseID,         taueta, eleeta, tauphi, elephi, DRCut)
                tauCleanAgainstMu = anautil.jetcleaning(
                    tau_eta2p3_iDLdm_pt18, mu_pt10_eta2p4_looseID_looseISO, taueta, mueta,  tauphi, muphi,  DRCut)
                tauCleaned = boolutil.logical_AND_List3(
                    tau_eta2p3_iDLdm_pt18, tauCleanAgainstEle, tauCleanAgainstMu)
                pass_tau_index_cleaned_DRBased = boolutil.WhereIsTrue(
                    tauCleaned)
                if debug_:
                    print "pass_tau_index_cleaned_DRBased", pass_tau_index_cleaned_DRBased


            # -------------------------------------------------------------
            st_runId[0] = long(run)
            st_lumiSection[0] = lumi
            st_eventId[0] = event
            st_isData[0] = isData

            st_isak4JetBasedHemEvent[0] =isak4JetBasedHemEvent
            st_isak8JetBasedHemEvent[0] =isak8JetBasedHemEvent
            st_ismetphiBasedHemEvent1[0]=ismetphiBasedHemEvent1
            st_ismetphiBasedHemEvent2[0]=ismetphiBasedHemEvent2

            st_prefiringweight[0] = prefiringweight_
            st_prefiringweightup[0] = prefiringweightup_
            st_prefiringweightdown[0] = prefiringweightdown_

            st_eletrigdecision[0] = eletrigdecision
            st_mutrigdecision[0] = mutrigdecision
            st_mettrigdecision[0] = mettrigdecision
            st_photrigdecision[0] = photrigdecision
            st_filterstatus[0] = filterdecision

            st_pfMetSmearPt[0] = met_smear
            st_pfMetCorrPt[0] = type1met_
            st_pfMetCorrPhi[0] = type1metphi_
            st_METXYCorr_Met[0] = METXYCorr_Met_MetPhi[0]
            st_METXYCorr_MetPhi[0] = METXYCorr_Met_MetPhi[1]
            st_pfMetCorrSig[0] = metCorrSig
            st_pfpatCaloMETPt[0] = patCaloMETPt
            st_pfpatCaloMETPhi[0] = patCaloMETPhi
            st_pfTRKMETPt[0] = TRKMETPt_
            st_pfTRKMETPhi[0] = TRKMETPhi_

            st_pfMetUncJetResUp.clear()
            st_pfMetUncJetResDown.clear()

            st_pfMetUncJetEnUp.clear()
            st_pfMetUncJetEnDown.clear()

            st_THINjetPx.clear()
            st_THINjetPy.clear()
            st_THINjetPz.clear()
            st_THINjetEnergy.clear()
            st_THINjetDeepCSV.clear()
            st_THINjetHadronFlavor.clear()
            st_THINjetNHadEF.clear()
            st_THINjetCHadEF.clear()

            st_THINjetCEmEF.clear()
            # st_THINjetPhoEF.clear()
            # st_THINjetEleEF.clear()
            # st_THINjetMuoEF.clear()
            st_THINjetNEmEF.clear()
            st_THINjetCMulti.clear()
            st_THINjetNMultiplicity.clear()
            st_THINjetCorrUnc.clear()
            st_THINbRegNNResolution.clear()
            st_THINbRegNNCorr.clear()
            st_THINPUjetIDLoose.clear()
            st_THINPUjetIDMedium.clear()
            st_THINPUjetIDTight.clear()
            st_THINjetUncSources.clear()
            st_THINjetUncTotal.clear()

            st_fjetPx.clear()
            st_fjetPy.clear()
            st_fjetPz.clear()
            st_fjetEnergy.clear()
            st_fjetDoubleSV.clear()
            st_fjetProbQCDb.clear()
            st_fjetProbHbb.clear()
            st_fjetProbQCDc.clear()
            st_fjetProbHcc.clear()
            st_fjetProbHbbc.clear()
            st_fjetProbbbvsLight.clear()
            st_fjetProbccvsLight.clear()
            st_fjetProbTvsQCD.clear()
            st_fjetProbWvsQCD.clear()
            st_fjetProbZHbbvsQCD.clear()
            st_fjetSDMass.clear()
            st_fjetSDMassCorrFact.clear()
            st_fjetN2b1.clear()
            st_fjetN2b2.clear()
            st_fjetTau21.clear()
            st_fjetCHSPRMass.clear()
            st_fjetCHSSDMass.clear()
            st_fjetjetUncSources.clear()
            st_fjetjetUncTotal.clear()

            '''
            st_Taudisc_againstLooseMuon.clear()
            st_Taudisc_againstTightMuon.clear()
            st_Taudisc_againstLooseElectron.clear()
            st_Taudisc_againstMediumElectron.clear()
            st_tau_isoLoose.clear()
            st_tau_isoMedium.clear()
            st_tau_isoTight.clear()
            st_tau_dm.clear()
            '''

            st_elePx.clear()
            st_elePy.clear()
            st_elePz.clear()
            st_eleEnergy.clear()
            st_eleIsPassTight.clear()
            st_eleIsPassLoose.clear()
            st_eleCharge.clear()

            st_muPx.clear()
            st_muPy.clear()
            st_muPz.clear()
            st_muEnergy.clear()
            st_isTightMuon.clear()
            st_muCharge.clear()
            #st_muIso.clear()

            st_phoPx.clear()
            st_phoPy.clear()
            st_phoPz.clear()
            st_phoEnergy.clear()
            st_phoIsPassTight.clear()

            # st_genParId.clear()
            # st_genMomParId.clear()
            # st_genParSt.clear()
            # st_genParPx.clear()
            # st_genParPy.clear()
            # st_genParPz.clear()
            # st_genParEnergy.clear()
            # st_METXYCorr_Met_MetPhi.clear()
            # st_METXYCorr_Met_MetPhi.clear()
            st_genParPt.clear()
            st_genParSample.clear()


            st_THINnJet[0] = len(pass_jet_index_cleaned)
            for ithinjet in pass_jet_index_cleaned:
                st_THINjetPx.push_back(ak4px_[ithinjet])
                st_THINjetPy.push_back(ak4py_[ithinjet])
                st_THINjetPz.push_back(ak4pz_[ithinjet])
                st_THINjetEnergy.push_back(ak4e_[ithinjet])
                st_THINjetDeepCSV.push_back(ak4deepcsv_[ithinjet])
                st_THINjetHadronFlavor.push_back(int(ak4flavor_[ithinjet]))
                st_THINjetCEmEF.push_back(ak4CEmEF_[ithinjet])
                # st_THINjetPhoEF.push_back(ak4PhEF_[ithinjet])
                # st_THINjetEleEF.push_back(ak4EleEF_[ithinjet])
                # st_THINjetMuoEF.push_back(ak4MuEF_[ithinjet])
                st_THINjetCHadEF.push_back(ak4CHadEF_[ithinjet])
                st_THINjetNEmEF.push_back(ak4NEmEF_[ithinjet])
                st_THINjetNHadEF.push_back(ak4NHadEF_[ithinjet])
                st_THINjetCMulti.push_back(ak4CMulti_[ithinjet])
                st_THINjetNMultiplicity.push_back(ak4NMultiplicity_[ithinjet])
                st_THINjetCorrUnc.push_back(ak4JEC_[ithinjet])
                st_THINbRegNNResolution.push_back(ak4bRegNNResolution[ithinjet])
                st_THINbRegNNCorr.push_back(ak4bRegNNCorr[ithinjet])
                st_THINPUjetIDLoose.push_back(ak4PUJetIDLoose[ithinjet] or ak4pt[ithinjet] > 50)
                st_THINPUjetIDMedium.push_back(ak4PUJetIDMedium[ithinjet] or ak4pt[ithinjet] > 50)
                st_THINPUjetIDTight.push_back(ak4PUJetIDTight[ithinjet] or ak4pt[ithinjet] > 50)
                
                temp_vecotor.clear()
                for jecsource in ak4jetUncSources[ithinjet]:
                    temp_vecotor.push_back(jecsource)
                st_THINjetUncSources.push_back(temp_vecotor) 
                st_THINjetUncTotal.push_back(ak4jetUncTotal[ithinjet])
                


                #print 'ak4px_',ak4px_[ithinjet],'ak4py_',ak4py_[ithinjet],'ak4pz_',ak4pz_[ithinjet]
                #print 'ak4e_',ak4e_[ithinjet]
                #print 'ak4deepcsv_',ak4deepcsv_[ithinjet]
            #print 'pass_jet_index_cleaned',pass_jet_index_cleaned
            #print 'st_THINjetDeepCSV',len(st_THINjetDeepCSV)
            #print 'st_THINnJet',st_THINnJet
            if debug_:
                print 'njets: ', len(pass_jet_index_cleaned)

            st_nfjet[0] = len(pass_fatjet_index_cleaned)
            for ifjet in pass_fatjet_index_cleaned:
                st_fjetPx.push_back(fatjetPx[ifjet])
                st_fjetPy.push_back(fatjetPy[ifjet])
                st_fjetPz.push_back(fatjetPz[ifjet])
                st_fjetEnergy.push_back(fatjetEnergy[ifjet])
                st_fjetDoubleSV.push_back(fatjet_DoubleSV[ifjet])
                st_fjetProbQCDb.push_back(fatjet_probQCDb[ifjet])
                st_fjetProbHbb.push_back(fatjet_probHbb[ifjet])
                st_fjetProbQCDc.push_back(fatjet_probQCDc[ifjet])
                st_fjetProbHcc.push_back(fatjet_probHcc[ifjet])
                st_fjetProbHbbc.push_back(fatjet_probHbbc[ifjet])
                st_fjetProbbbvsLight.push_back(fatjet_prob_bbvsLight[ifjet])
                st_fjetProbccvsLight.push_back(fatjet_prob_ccvsLight[ifjet])
                st_fjetProbTvsQCD.push_back(fatjet_prob_TvsQCD[ifjet])
                st_fjetProbWvsQCD.push_back(fatjet_prob_WvsQCD[ifjet])
                st_fjetProbZHbbvsQCD.push_back(fatjet_prob_ZHbbvsQCD[ifjet])
                st_fjetSDMass.push_back(fatjetSDmass[ifjet])
                st_fjetSDMassCorrFact.push_back(SDMassCorrFact[ifjet])
                st_fjetN2b1.push_back(fatN2_Beta1_[ifjet])
                st_fjetN2b2.push_back(fatN2_Beta2_[ifjet])
                st_fjetTau21.push_back(fatjetTau2[ifjet]/fatjetTau1[ifjet])
                st_fjetCHSPRMass.push_back(fatjetCHSPRmassL2L3Corr[ifjet])
                st_fjetCHSSDMass.push_back(fatjetCHSSDmassL2L3Corr[ifjet])
                temp_vecotor.clear()
                for jecsource in fatjetUncSources[ifjet]:
                    temp_vecotor.push_back(jecsource)
                st_fjetjetUncSources.push_back(temp_vecotor) 
                st_fjetjetUncTotal.push_back(fatjetUncTotal[ifjet])
                #print ("fatN2_Beta1_",fatN2_Beta1_[ifjet],"fatN2_Beta2_",fatN2_Beta2_[ifjet])

            st_nEle[0] = len(pass_ele_loose_index)
            for iele in pass_ele_loose_index:
                st_elePx.push_back(elepx_[iele])
                st_elePy.push_back(elepy_[iele])
                st_elePz.push_back(elepz_[iele])
                st_eleEnergy.push_back(elee_[iele])
                st_eleIsPassLoose.push_back(bool(elelooseid_[iele]))
                st_eleIsPassTight.push_back(bool(ele_pt30_eta2p5_tightID[iele]))
                st_eleCharge.push_back(eleCharge_[iele])
            if debug_:
                print 'nEle: ', len(pass_ele_loose_index)

            st_nMu[0] = len(pass_mu_index)
            for imu in pass_mu_index:
                st_muPx.push_back(mupx_[imu])
                st_muPy.push_back(mupy_[imu])
                st_muPz.push_back(mupz_[imu])
                st_muEnergy.push_back(mue_[imu])
                st_isTightMuon.push_back(
                    bool(mutightid_[imu]) and muisotight[imu])
                st_muCharge.push_back(muCharge_[imu])
                #st_muIso.push_back(muIso_[imu])
            if debug_:
                print 'nMu: ', len(pass_mu_index)

            st_nTau_DRBased_EleMuVeto[0] = len(pass_tau_index_cleaned_DRBased)
            st_nTau_discBased_looseElelooseMuVeto[0] = len(
                tau_eta2p3_iDLdm_pt18_looseEleVeto_looseMuVeto_index)
            st_nTau_discBased_looseEleTightMuVeto[0] = len(
                tau_eta2p3_iDLdm_pt18_looseEleVeto_tightMuVeto_index)
            st_nTau_discBased_mediumElelooseMuVeto[0] = len(
                tau_eta2p3_iDLdm_pt18_mediumEleVeto_looseMuVeto_index)
            st_nTau_discBased_TightElelooseMuVeto[0] = len(
                tau_eta2p3_iDLdm_pt18_tightEleVeto_looseMuVeto_index)
            st_nTau_discBased_TightEleTightMuVeto[0] = len(
                tau_eta2p3_iDLdm_pt18_tightEleVeto_tightMuVeto_index)
            if debug_:
                print 'nTau: ', len(pass_tau_index_cleaned_DRBased)
            #print 'nTau: ',len(pass_tau_index_cleaned_DRBased),'event',event
            '''
            for itau in pass_tau_index_cleaned:
                st_Taudisc_againstLooseMuon.push_back(bool(Taudisc_againstLooseMuon[itau]))
                st_Taudisc_againstTightMuon.push_back(bool(Taudisc_againstTightMuon[itau]))
                st_Taudisc_againstLooseElectron.push_back(bool(Taudisc_againstLooseElectron[itau]))
                st_Taudisc_againstMediumElectron.push_back(bool(Taudisc_againstMediumElectron[itau]))
                st_tau_isoLoose.push_back(bool(tau_isLoose_[itau]))
                st_tau_isoMedium.push_back(bool(tau_isoMedium_[itau]))
                st_tau_isoTight.push_back(bool(tau_isoTight_[itau]))
                st_tau_dm.push_back(bool(tau_dm_[itau]))
            '''

            st_nPho[0] = len(pass_pho_index_cleaned)
            for ipho in pass_pho_index_cleaned:
                st_phoPx.push_back(phopx_[ipho])
                st_phoPy.push_back(phopy_[ipho])
                st_phoPz.push_back(phopz_[ipho])
                st_phoEnergy.push_back(phoe_[ipho])
                st_phoIsPassTight.push_back(bool(photightID_[ipho]))
            if debug_:
                print 'nPho: ', len(pass_pho_index)

            st_pu_nTrueInt[0] = pu_nTrueInt_
            st_pu_nPUVert[0] = pu_nPUVert_
            st_THINjetNPV[0] = ak4NPV_

            #st_nGenPar[0] =  nGenPar_
            genpar_pt = GenPtProd.GenPtProducer(
                samplename, nGenPar_, genParId_, genMomParId_, genParSt_, genpx_, genpy_)

            ## ----------------------- TOP MATCHING ------------------------------------------------------------------
            ## need this new branch only for the top samples, for remaining it will always contain a string "notTop"
            ## -------------------------------------------------------------------------------------------------------

            #topmatchStr = [0:"notTopOrNotAK8",1:"notTop", 2:"TopMatched", 3:"Wmatched", 4:"Wunmatched" ]
            topmatchStr = 0
            if (samplename == 6) and ("SemiLeptonic" in outfilename):
                if len(pass_fatjet_index_cleaned) > 0:
                    fjidx = pass_fatjet_index_cleaned[0]
                    topmatchStr = GenPtProd.GenMatchTop(samplename, nGenPar_, genParId_, genMomParId_, genParSt_, genpx_, genpy_, genpz_, fatjetPx[fjidx], fatjetPy[fjidx], fatjetPz[fjidx])
            #print " topmatchStr for this event is ", topmatchStr

            st_TopMatching[0] = topmatchStr

            for i in range(len(genpar_pt)):
                st_genParPt.push_back(genpar_pt[i])
            st_genParSample.push_back(samplename)

            # for igp in range(nGenPar_):
            #     st_genParId.push_back(int(genParId_[igp]))
            #     st_genMomParId.push_back(int(genMomParId_[igp]))
            #     st_genParSt.push_back(int(genParSt_[igp]))
            #     st_genParPx.push_back(genpx_[igp])
            #     st_genParPy.push_back(genpy_[igp])
            #     st_genParPz.push_back(genpz_[igp])
            #     st_genParEnergy.push_back(gene_[igp])
            if debug_:
                print 'nGen: ', nGenPar_

            scale_temp = []
            pdf_temp = []
            if len(pdfscaleSysWgtID) > 0:
                for i in range(0,9):
                    scale_temp.append(pdfscaleSysWeights[i])
                for i in range(9, len(pdfscaleSysWgtID)):
                    pdf_temp.append(pdfscaleSysWeights[i])
            else:
                scale_temp.append(1.0)
                pdf_temp.append(1.0)

            st_scaleWeightUP[0] = max(scale_temp)
            st_scaleWeightDOWN[0] = min(scale_temp)
            st_pdfWeightUP[0] = max(pdf_temp)
            st_pdfWeightDOWN[0] = min(pdf_temp)

            st_pfMetUncJetResUp.push_back(metUnc_[0])
            st_pfMetUncJetResDown.push_back(metUnc_[1])
            st_pfMetUncJetEnUp.push_back(metUnc_[2])
            st_pfMetUncJetEnDown.push_back(metUnc_[3])

            outTree.Fill()

    #outfile = TFile(outfilenameis,'RECREATE')
    outfile.cd()
    h_total_mcweight.Write()
    h_total.Write()
    h_eventCounter.Write()
    outfile.Write()
    print "output written to ", outfilename
    end = time.clock()
    print "%.4gs" % (end-start)


if __name__ == '__main__':
    if not runInteractive:
        txtFile = infile

        runbbdm(txtFile)

    if runInteractive and runOnTxt:
	filesPath = dirName+'/*txt'
	files = glob.glob(filesPath)
        n = 1  # submit n txt files at a time, make equal to cores
        final = [files[i * n:(i + 1) * n]
                 for i in range((len(files) + n - 1) // n)]
        print 'final', final
        for i in range(len(final)):
            print 'first set', final[i]

            try:
                pool = mp.Pool(1)
                pool.map(runbbdm, final[i])
                pool.close()
                pool.join()
	    except Exception as e:
		print e
		print "Corrupt file inside input txt file is detected! Skipping this txt file:  ", final[i]
		continue

    if runInteractive and not runOnTxt:
        ''' following part is for interactive running. This is still under testing because output file name can't be changed at this moment '''
        inputpath = "/eos/cms/store/group/phys_exotica/bbMET/ExoPieElementTuples/MC_2017miniaodV2_V1/"

        os.system('rm dirlist.txt')
        os.system("ls -1 "+inputpath+" > dirlist.txt")

        allkeys = [idir.rstrip() for idir in open('dirlist.txt')]
        alldirs = [inputpath+"/"+idir.rstrip() for idir in open('dirlist.txt')]

        pool = mp.Pool(6)
        allsample = []
        for ikey in allkeys:
            dirpath = inputpath+"/"+ikey
            txtfile = ikey+".txt"
            os.system("find "+dirpath +
                      "  -name \"*.root\" | grep -v \"failed\"  > "+txtfile)
            fileList = TextToList(txtfile)
            ## this is the list, first element is txt file with all the files and second element is the ikey (kind of sample name identifier)
            sample_ = [txtfile, ikey]
            ## push information about one sample into global list.
            allsample.append(sample_)
        print allsample
        pool.map(runbbdm, allsample)
        ## this works fine but the output file name get same value becuase it is done via a text file at the moment, need to find a better way,
