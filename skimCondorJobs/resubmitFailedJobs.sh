#!/bin/sh
dateAndtime=`date +'%Y-%m-%d-%H-%M-%S'`

stringSearch="written"
oldSubmitDir="tempFilelists_2022-10-13-12-19-26" #change this to be your tempFilelists that you have submitted and you want to resubmit
newDir="Filelists_resubmit_${dateAndtime}"
mkdir -p $newDir

firstjobId="2097430" #change this to be the FIRST job Id of your oldSubmitDir; you can check your logsubmit.txt
lastjobId="2097783"  #change this to be the LAST job Id of your oldSubmitDir; you can check your logsubmit.txt

for file in `ls output`; do
    #echo $file
    if ! grep -q $stringSearch output/$file; then
        #echo $file
        jobid=`echo $file | cut -d '.' -f 2-3`
        jobcluster=`echo $file | cut -d '.' -f 2`
        if [[ "$jobcluster" -gt $firstjobId && "$jobcluster" -lt $lastjobId ]]; then
            #submitdate=`echo $oldSubmitDir | cut -d '_' -f 2 | cut -d '-' -f 1-3`
            #if grep $submitdate log/condor.$jobid.log; then
                failedTxt=`grep -hnr "running" output/$file | rev | cut -d ' ' -f 1 | rev`
                echo $file $failedTxt
                cp $oldSubmitDir/$failedTxt $newDir
            #fi
        fi
    fi
done

newtext="folder=\"${newDir}\""
sed -i "2s/.*/${newtext}/" MultiResubmit.py

#resubmit condor jobs
#nohup python -u MultiResubmit.py &> resubmit_logsubmit_$dateAndtime.txt &