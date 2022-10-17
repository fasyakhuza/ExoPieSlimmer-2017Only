import os, datetime
folder="Filelists_2017Bkg_ForFasya_Resubmit"
test=False

listfiles = [f for f in os.listdir(folder) if f.endswith('.txt')]

if not test: os.system("chmod +x runAnalysis.sh")
for outdirs in ['error','log','output']:
    os.system("mkdir -p "+outdirs)

count=1

def submitjob(jobcount,fname):
    global count
    submittemp=open("submit_multi_temp.sub","w")
    submitfile=open("submit_multi.sub","r")
    for line in submitfile:
        if line.startswith('transfer_input_files'):
            submittemp.write(line.strip()+', '+folder+'/'+fname+'\n')
        else:
            submittemp.write(line)
    submitfile.close()

    #submittemp.write("arguments = "+tempfile.split('/')[1]+" "+fname.split('.')[0]+" "+str(jobcount)+" "+tempfile.split('/')[1].replace('.txt','.root')+'\nqueue')
    submittemp.write("\narguments = "+fname+" "+fname.split('.')[0]+" "+str(jobcount)+" "+fname.replace('.txt','.root')+" $(Proxy_path)"+"\nqueue")
    #submittemp.write("\narguments = "+tempfile+" "+fname.split('.')[0]+" "+str(jobcount)+" "+tempfile.split('/')[1].replace('.txt','.root')+" $(Proxy_path)"+"\nqueue")
    #submittemp.write("transfer_output_remaps = \"BROutput.root = BR_Outputs/Output_"+fname.split('.')[0]+"_"+str(jobcount)+".root\"\nqueue")
    submittemp.close()

    print ("\n===============================\nSubmitting jobs #"+str(count)+": "+ fname.split('.')[0]+"\n===============================\n")

    if not test: os.system("condor_submit submit_multi_temp.sub")
    count+=1

for fname in listfiles:
    jobcount=0
    f=open(folder+"/"+fname,'r')
    submitjob(jobcount,fname)
    #jobcount+=1
    f.close()

print ("\nDone. Submitted "+str(count-1)+" jobs.")
