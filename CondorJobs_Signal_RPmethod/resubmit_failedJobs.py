import os
from glob import glob

test=False

count=1

def submitjob(count,txtfile):
    #global count
    submittemp=open("submit_multi_resubmit.sub","w")
    submitfile=open("submit_multi.sub","r")
    for line in submitfile:
        if line.startswith('transfer_input_files'):
            submittemp.write(line.strip()+', '+txtfile+'\n')
        else:
            submittemp.write(line)
    submitfile.close()
    dummy='dummy'
    submittemp.write("arguments = "+txtfile.split('/')[-1]+" "+dummy+" "+dummy+"  "+txtfile.split('/')[-1].replace('.txt','.root')+'\nqueue')
    submittemp.close()


    print "\n===============================\nSubmitting jobs #"+str(count)+": "+ txtfile+"\n===============================\n"

    if not test: os.system("condor_submit submit_multi_resubmit.sub")

    #count+=1

path='NewFiles'

files=glob(path+'/*txt')

for file in files:
    submitjob(count,file)
    count+=1



print 'Total number of jobs: ',count
