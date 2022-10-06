## Settings for submitting jobs to HTCondor. 

A set of scripts to submit jobs to HTCondor for slimming big tuples to smaller tuples


#### Setup skimCondorJobs
```
cd CMSSW_11_0_2/src/ExoPieSlimmer

git clone blablabla

cd skimCondorJobs

rm MultiSubmit.py submit_multi.sub runAnalysis.sh

wget multi

wget submulti

wget runAnalysis
```
download folderForYuehShun
```
scram b -j 4
```


## What changes to make: 

In order to run the skimmer, you have to change the input file path and also setinterative to True. 

isCondor = True

runInteractive = False

inputpath= "/eos/cms/store/group/phys_exotica/bbMET/ExoPieElementTuples/MC_2017miniaodV2_V1/" in MultiSubmit.py

proxypath in runAnalysis.sh


#### Submit Jobs to HTCondor
```
cmsenv

voms-proxy-init --voms cms --valid 192:00 && cp -v /tmp/x509up_xxxxxxx /afs/cern.ch/usernameinitial/yourusername/private/x509up

. submitjob.sh
```


## How to run the skimmer 

#### Intractive 1: 
if you want to run skimmer on txt files of datasets, then use this command:
```
python SkimTree.py -F -inDir inputdirectory_name_where_txt_files_are_located -runOnTXT -D outputDirectory_name
```
but you need to keep `isCondor=False` and `runInteractive=True`

#### Intractive 2:
if you want to run skimmer on eos path then use this command:
```
python SkimTree.py -F -inDir inputdirectory_name_where_txt_files_are_located -D outputDirectory_name
```
Note: this command is not fully tested so please don't use for now. We need to make few changes.

In case you want to use this command, you need to do following things:
1. Inside the function runbbdm(), you need to this condition `if runInteractive:` into two conditions ` if runInteractive and not runOnTxt:` and ` if runInteractive and runOnTxt: ` for the outfilename . 

#### Submitting Condor Job,

To submit condor jobs, please follow these steps:
```
git clone git@github.com:ExoPie/ExoPieSlimmer.git
git clone git@github.com:ExoPie/ExoPieUtils.git
cd ExoPieSlimmer
git clone https://github.com/deepakcern/CondorJobs.git
cd CondorJobs
. submitjobs.sh
```
Before running this command please make few changes:
keep `isCondor=True` and `runInteractive=False`

replace this `infile_  = TextToList(txtfile[0])` with `infile_  = TextToList(txtfile)` , comment this `key_=txtfile[1]` and replace this `outfilename= prefix+key_+".root"` with `SkimmedTree.root`

Filelists are already there, so you need to replace them with your Filelists


## some details 

variables.py: variables form input files are listed here

triggers.py: trigger list

outputTree.py: branches to be saved in the tree (output)

filters.py: event filter (met) 

SkimTree.py: main file 
