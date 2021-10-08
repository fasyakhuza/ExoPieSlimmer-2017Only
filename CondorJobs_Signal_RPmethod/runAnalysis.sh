#!/bin/sh
#### FRAMEWORK SANDBOX SETUP ####
# Load cmssw_setup function
export SCRAM_ARCH=slc6_amd64_gcc700
source ./cmssw_setup.sh

# Setup CMSSW Base
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

# Download sandbox
#wget --no-check-certificate "http://stash.osgconnect.net/+ptiwari/sandbox-CMSSW_8_0_26_patch1-76efecd.tar.bz2"

# Setup framework from sandbox
#cmssw_setup sandbox-CMSSW_10_3_0-4cef61e.tar.bz2

scramv1 project CMSSW_10_3_0
cd CMSSW_10_3_0/src
eval `scramv1 runtime -sh`

#cd $CMSSW_BASE
#cmsenv
cd ../../

python bbDM_2HDMa_Signal_rp.py "$1" 2017

IFS='.'
read -a strout <<< "$4"
outfile_=$strout*"root"
files=$(ls $outfile_ | wc -l)
outfile=($outfile_)

if [[ $files > 0 ]]; then
    for i in "${outfile[@]}"; do
        echo "$i"
        until xrdcp -f "$i" root://eoscms.cern.ch//eos/cms/store/group/phys_exotica/bbMET/2017_SkimmedFiles/skim_v17_08_00_METXY_SIG/"$i"; do
            sleep 60
            echo "Retrying"
        done
    done
fi

exitcode=$?

if [[ $files < 0 ]]
then
    echo "Error: The python script failed, could not create the output file."
fi

exit $exitcode
