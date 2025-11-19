"""
script to extra data from scans and place into table for a simple record of the scans of interest performed during the experiment. 
"""
import os
from pathlib import Path
import pandas as pd
import nexusformat.nexus as nx
from datetime import datetime
import numpy as np
import argparse
from progress.bar import Bar
import re

def check_endstation(scan_command):
    """
    check which endstation scan was on, use 'ca35b' as flag for ES1
    """
    if 'ca35b' in scan_command:
        return 1
    return 2

def get_manipulator_pos(filedata,endstation):
    """
    parse manipulator positions from file, using filedata, and endstation value
    """
    xyz_keys={1:['sm21b_x','sm21b_y','sm21b_z'],
              2: ['sm52b_XP','sm52b_YP','sm52b_ZP','RotY']}
    manipkeys=xyz_keys[endstation]
    manipvalues=[f"{key}: {filedata.entry.instrument[key].value}" for key in manipkeys]
    if len(manipvalues)==3:
        manipvalues.append("N/A")
    return manipvalues

def get_slit_pos(filedata):
    """
    parse slit settings
    """
    key='s4b_ygapsize'
    val=float(filedata.entry.instrument[key].value)
    return f"{key} : {val}"

def get_datetime_str(filedata):
    """
    parse isoformat datetime in readable string
    """
    dt_object=datetime.fromisoformat(filedata.entry.start_time.nxdata.decode())
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")


def get_pgm_energy_info(filedata,col_names,scan_command,scan_type):
    """
    parse data from a pgm_energy scan
    """
    full_info={}
    full_info['scan_command']=scan_command.split(' ')
    precision=0
    energy_vals=np.array(filedata.entry.instrument.pgm_energy.value)
    full_info['E_start']=round(energy_vals[0],precision)
    full_info['E_end']=round(energy_vals[-1],precision)
    full_info['Endstation']=check_endstation(full_info['scan_command'])
    
    full_info['datetime']=get_datetime_str(filedata)
    full_info.update({k:v for k,v in zip(['X','Y','Z','Rot'],get_manipulator_pos(filedata,full_info['Endstation']))})
    full_info['Slits']=get_slit_pos(filedata)
    full_info['Scan_type']=scan_type
    return [str(full_info[col]) if col in full_info.keys() else 'N/A' for col in col_names]


def scan_not_implemented(filedata,col_names,scan_command,scan_type):
    """
    return minimal information about scan and show not implemented value
    """
    scantypelist=[scan_type,get_datetime_str(filedata)]
    nalist=['Not implemented']*(len(col_names)-1)
    return scantypelist  + nalist


def get_row_data(filedata,col_names):
    """
    obtain data from file to fill requested columns in log
    """
    functions={'pgm_energy':get_pgm_energy_info}
    scan_command=filedata.entry.scan_command.nxdata.decode()
    scan_type=scan_command.split(' ')[1]
    info_func=scan_not_implemented
    not_implemented=1
    if scan_type in functions.keys():
        info_func=functions[scan_type]
        not_implemented=0
    row_out=info_func(filedata,col_names,scan_command,scan_type)
    return row_out,not_implemented



def save_log(dirpath: Path, col_names: list, outpath: Path):
    """
    create file list of all .nxs files, parse data from each .nxs file and write data to log file
    """
    nxs_list=[file for file in os.listdir(dirpath) if file.endswith('.nxs')]
    nxs_list.sort()
    bar = Bar('Processing', max=len(nxs_list))
    not_implemented_count=0
    with open(outpath,"w") as f:
        col_string='\t'.join(col_names)
        f.write(f"Scan\t{col_string}\n")
        for file in nxs_list:
            filedata=nx.nxload(dirpath/file)
            row_data,not_imp_val=get_row_data(filedata,col_names=col_names)
            row_string='\t'.join(row_data)
            f.write(f"{file.split('.nxs')[0]}\t{row_string}\n")
            bar.next()
            not_implemented_count+=not_imp_val
            #fulltable.loc[file.split('.nxs')[0]]=row_data
    bar.finish()
    
    if not_implemented_count>0:
        print(f"WARNING: {not_implemented_count} files were found to have scan_types not implemented in the log creator")
    print(f"saved sample log to :  {str(outpath)}")
    return 

def main():
    HELP_STR=(
        "Takes in a directory or directory/subfolder path and creates a scan log exporting to csv"
    )
    parser=argparse.ArgumentParser(description=HELP_STR)

    HELP_STR= (
        'enter directory or directory/subfolder path for the experiment you want to create the scan log for'
    )
    parser.add_argument('-dir',"--dir_path",help=HELP_STR)

    HELP_STR= (
        'enter the directory path where you want to save the .csv file'
    )
    parser.add_argument('-out',"--out_path",default=None,help=HELP_STR)

    HELP_STR = (
        "use this argument to specify which columns you would like in your data. Defaults to ['datetime','E_start', 'E_end', 'Endstation','X','Y','Z','Rot','Slits']"
    )
    parser.add_argument("-cols","--col_names",default=['Scan_type','datetime','E_start', 'E_end', 'Endstation','X','Y','Z','Rot','Slits'],help=HELP_STR)


    args=parser.parse_args()
    dir=args.dir_path
    cols=args.col_names
    dirpath=Path(dir)
    if args.out_path:
        outpath=Path(args.out_path)
    else:
        outpath=dirpath
    
    exp_num_matches=re.findall(r"[a-zA-Z]{2}\d{5}-\d",dir)
    outfile=outpath/f"{exp_num_matches[0]}_sample_log.csv"
    save_log(dirpath,cols,outfile)

if __name__ == '__main__':
    main()