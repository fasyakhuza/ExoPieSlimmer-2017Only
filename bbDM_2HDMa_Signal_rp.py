import os
import sys

mA_list = [600,1200]
ma_list = [10,50,100,150,200,250,300,350,400,450,500,700,750,1000]

inpuFile = sys.argv[1]
year = sys.argv[2]
for mA_ in mA_list:
    for ma_ in ma_list:
        if ma_ < mA_:
            os.system('python SkimTree.py -F -i '+str(inpuFile)+' --bbdm_2hdma --mA '+str(mA_)+' --ma '+str(ma_)+' -y '+str(year))
