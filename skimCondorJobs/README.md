# Settings for submitting jobs to HTCondor. 

A set of scripts to submit jobs to HTCondor for slimming big tuples to smaller tuples


### Setup skimCondorJobs
```
cd CMSSW_11_0_2/src/ExoPieSlimmer

git clone https://github.com/tiwariPC/skimCondorJobs.git

cd skimCondorJobs

rm MultiSubmit.py submit_multi.sub runAnalysis.sh

wget https://raw.githubusercontent.com/fasyakhuza/ExoPieSlimmer-2017Only/Skim_V0_2017Only/skimCondorJobs/MultiSubmit.py

wget https://raw.githubusercontent.com/fasyakhuza/ExoPieSlimmer-2017Only/Skim_V0_2017Only/skimCondorJobs/submit_multi.sub

wget https://raw.githubusercontent.com/fasyakhuza/ExoPieSlimmer-2017Only/Skim_V0_2017Only/skimCondorJobs/runAnalysis.sh
```
Then, download the folder ```Filelists_2017Bkg_ForYuehShun``` in this github
```
scram b -j 4
```


### Changes to be done in executing files.

Change the folder name in ```line 2``` of ```MultiSubmit.py``` file to ```Filelists_2017Bkg_ForYuehShun```.

Change the ```Proxy_path``` in ```line 3``` of submit_multi.sub file to be your proxy path.

Open the ```SkimTree.py``` file  and change ```isCondor = False``` to ```isCondor = True```.


### Submit the condor jobs

Finally run

```
cmsenv

voms-proxy-init --voms cms --valid 192:00 && cp -v /tmp/x509up_xxxxxxx /afs/cern.ch/user/usernameinitial/yourusername/private/x509up

. submitjobs.sh
```

Condor Jobs will be submitted with this file.

Run the following command to see the status:

```tail -f logsubmit.txt```




# Settings for REsubmitting jobs to HTCondor.

First, download the executing files

```
wget https://raw.githubusercontent.com/fasyakhuza/ExoPieSlimmer-2017Only/Skim_V0_2017Only/skimCondorJobs/MultiResubmit.py

wget https://raw.githubusercontent.com/fasyakhuza/ExoPieSlimmer-2017Only/Skim_V0_2017Only/skimCondorJobs/resubmitFailedJobs.sh
```

### Changes to be done in executing files for resubmission

Change the folder name in ```line 5``` of ```resubmitFailedJobs.sh``` file to be your ```tempFilelists_YYYY-mm-dd-HH-MM-SS``` folder name that you have submitted and you want to resubmit

Change the FIRST job Id in ```line 9``` of ```resubmitFailedJobs.sh``` file to be your FIRST job Id of ```tempFilelists_YYYY-mm-dd-HH-MM-SS```; you can check the job id in your ```logsubmit.txt```

Change the LAST job Id in ```line 10``` of ```resubmitFailedJobs.sh``` file to be your LAST job Id of ```tempFilelists_YYYY-mm-dd-HH-MM-SS```; you can check the job id in your ```logsubmit.txt```


### Resubmit the failed jobs to HTCondor

Run

```
cmsenv

voms-proxy-init --voms cms --valid 192:00 && cp -v /tmp/x509up_xxxxxxx /afs/cern.ch/user/usernameinitial/yourusername/private/x509up

. resubmitFailedJobs.sh
```
