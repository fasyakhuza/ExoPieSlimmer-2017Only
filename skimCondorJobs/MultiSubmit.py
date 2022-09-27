import os, datetime
folder="Filelists_outtest"
test=False
maxfilesperjob=100

listfiles = [f for f in os.listdir(folder) if f.endswith('.txt')]

tempdir='tempFilelists_'+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
if not test: os.system("chmod +x runAnalysis.sh")
for outdirs in ['error','log','output',tempdir]:
    os.system("mkdir -p "+outdirs)

count=1

def submitjob(jobcount,fname,tempfile):
    global count
    submittemp=open("submit_multi_temp.sub","w")
    submitfile=open("submit_multi.sub","r")
    for line in submitfile:
        if line.startswith('transfer_input_files'):
            submittemp.write(line.strip()+', '+tempfile+'\n')
        else:
            submittemp.write(line)
    submitfile.close()

    #submittemp.write("arguments = "+tempfile.split('/')[1]+" "+fname.split('.')[0]+" "+str(jobcount)+" "+tempfile.split('/')[1].replace('.txt','.root')+'\nqueue')
    submittemp.write("\narguments = "+tempfile.split('/')[1]+" "+fname.split('.')[0]+" "+str(jobcount)+" "+tempfile.split('/')[1].replace('.txt','.root')+" $(Proxy_path)"+"\nqueue")
    #submittemp.write("transfer_output_remaps = \"BROutput.root = BR_Outputs/Output_"+fname.split('.')[0]+"_"+str(jobcount)+".root\"\nqueue")
    submittemp.close()

    print ("\n===============================\nSubmitting jobs #"+str(count)+": "+ fname.split('.')[0]+"_"+str(jobcount)+"\n===============================\n")

    if not test: os.system("condor_submit submit_multi_temp.sub")
    count+=1

for fname in listfiles:
    jobcount=0
    f=open(folder+"/"+fname,'r')
    newf=tempdir+'/'+fname.split('.')[0]+'_'+str(jobcount)+'.txt'
    fnew=open(newf,'w')
    linecount=0
    for line in f:
        fnew.write(line)
        linecount+=1

        if linecount==maxfilesperjob:
            fnew.close()
            submitjob(jobcount,fname,newf)
            jobcount+=1
            linecount=0
            newf=tempdir+'/'+fname.split('.')[0]+'_'+str(jobcount)+'.txt'
            fnew=open(newf,'w')
    fnew.close()
    if linecount>0: submitjob(jobcount,fname,newf)
    f.close()

print ("\nDone. Submitted "+str(count-1)+" jobs.")
