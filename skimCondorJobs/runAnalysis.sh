#!/bin/sh
#### FRAMEWORK SANDBOX SETUP ####
# Load cmssw_setup function
export SCRAM_ARCH=slc7_amd64_gcc700
source ./cmssw_setup.sh

# Setup CMSSW Base
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

#Proxy
export X509_USER_PROXY=$5
voms-proxy-info -all
voms-proxy-info -all -file $5

# Download sandbox
#wget --no-check-certificate "http://stash.osgconnect.net/+ptiwari/sandbox-CMSSW_8_0_26_patch1-76efecd.tar.bz2"

scramv1 project CMSSW_10_3_0
cd CMSSW_10_3_0/src
eval `scramv1 runtime -sh`

#cd $CMSSW_BASE
cmsenv
cd ../../

#dirpath="/eos/user/f/fkhuzaim/monoZtoLL/skimmedTree/"
dirpath="/eos/user/f/fkhuzaim/2017UL_BackgroundSamples_SkimmedFiles/"
dir=`echo $1 | rev | cut --complement -d '_' -f 1 | rev`
if [ -d "$dirpath$dir" ]; then
  echo "$dirpath$dir has existed"
else
  mkdir $dirpath$dir
fi

#echo "1 is $1"
python SkimTree.py -y 2017 -F -i "$1"

if [ -e "$4" ]; then
  #until xrdcp -f "$4" root://eoscms.cern.ch//eos/user/f/fkhuzaim/monoZtoLL/condor_test/"$4"; do
  #until xrdcp -f "$4" /eos/user/f/fkhuzaim/monoZtoLL/condor_test/"$4"; do
  until xrdcp -f "$4" $dirpath$dir/"$4"; do
    sleep 60
    echo "Retrying"
  done

fi

#exitcode=$?

if [ ! -e "$4" ]; then
  echo "Error: The python script failed, could not create the output file."

fi
#exit $exitcode
