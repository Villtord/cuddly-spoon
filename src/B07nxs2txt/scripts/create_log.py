"""
script to extract data from .nxs scans and place into table for 
a simple record of the scans of interest performed during the experiment. 
"""
import os
from pathlib import Path
import argparse
import re
from datetime import datetime
import numpy as np
from progress.bar import Bar
import nexusformat.nexus as nx
from nexusformat.nexus.tree import NeXusError


class b07_samplelog_parser():
    
    def __init__(self,dirpath,infile,outfile):
        self.file=infile
        self.outfile=outfile
        self.filedata=nx.nxload(dirpath/infile)
        self.scan_command=self.filedata['entry/scan_command']
        self.function_map={
            'Date': self.get_date_str,
            'Time': self.get_time_str,
            'Endstation': self.get_endstation,
            'Scan Number': self.get_scan_number,
            'Scan Type': self.get_scan_type,
            'Sample Name': self.get_sample_name,
            'NEXAFS Region': self.get_nexafs_regions,
            'XPS Region': self.get_xps_regions

        }
        self.standard_columns={
            'Scan Number': None,
            'Sample Name': None,	
            'Scan Type': None,	
            'NEXAFS Region': None,
            'XPS Region': None,
            'Photon Energy': 'entry/instrument/pgm_energy/value',
            'cff': 'entry/instrument/pgm_cff/value',
            'Endstation': None,
            's4b_Ygapsize': 'entry/instrument/s4b_xpagsize/value',
            'Scan Command': 'entry/scan_command',
            'sm21b_x': 'entry/instrument/sm21b_x/value',
            'sm21b_y': 'entry/instrument/sm21b_y/value',
            'sm21b_z': 'entry/instrument/sm21b_z/value',
            'sm21b_Rot': 'entry/instrument/sm21b_Rot/value',
            'sm52b_xp': 'entry/instrument/sm52b_xp/value',
            'sm52b_yp': 'entry/instrument/sm52b_yp/value',
            'sm52b_zp': 'entry/instrument/sm52b_zp/value',
            'sm52b_RotY': 'entry/instrument/sm52b_RotY/value',
            'sm52b_RotZ': 'entry/instrument/sm52b_RotZ/value',
            'm4b YBASE motor position': 'entry/instrument/m4b_y_base_positioner/value',
            'm5b YBASE motor position': 'entry/instrument/m4b_y_base_positioner/value',
            'Date': None,
            'Time': None
        }
    
    def check_nxroot_key(self,rootobj,path):
        """
        check if path exists in file
        
        :param rootobj: loaded nexus file data tree- type NXroot
        :param path: path of value to check
        """
        try:
            _ = rootobj[path]  
            return True
        except NeXusError:
            return False
        
    def save_header_data(self):
        column_list=self.standard_columns.keys()
        column_str='\t'.join(column_list)
        self.outfile.write(column_str+'\n')

    def save_row_data(self):
        outdata={}
        column_list=self.standard_columns.keys()
        keys_to_parse=[]
        for key,path in self.standard_columns.items():
            if path is None:
                keys_to_parse.append(key)
                continue
            if not self.check_nxroot_key(self.filedata,path):
                outdata[key]=''
                continue
            outdata[key]=f'{self.filedata[path]}'
        for key in keys_to_parse:
            infofunc=self.function_map[key]
            outdata[key]=infofunc()
        out_row=[str(outdata[key]) for key in column_list]
        self.outfile.write('\t'.join(out_row)+'\n')
        return
    
    def get_scan_type(self):
        if 'dummy_a 0 0 1' in self.scan_command:
          return 'XPS'
        if 'pgm_energy' in self.scan_command:
          return 'NEXAFS'
        return ''

    def get_endstation(self):
        """
        check which endstation scan was on, use 'ca35b' as flag for ES1
        """
        if 'ca35b' in self.scan_command:
            return 2
        return 1

    def get_date_str(self):
        """
        parse isoformat datetime in readable date string
        """
        dt_object=datetime.fromisoformat(self.filedata.entry.start_time.nxdata.decode())
        return dt_object.strftime("%Y-%m-%d")

    def get_time_str(self):
        """
        parse isoformat datetime in readable time string
        """
        dt_object=datetime.fromisoformat(self.filedata.entry.start_time.nxdata.decode())
        return dt_object.strftime("%H:%M:%S")

    def get_scan_number(self):
        return f"{self.file.split('.nxs')[0]}"
    
    def get_nexafs_regions(self):
        if self.get_scan_type()=='NEXAFS':
            return str(self.filedata['entry/analyser/region_list'].astype(str))
        return ''
    
    def get_sample_name(self):
        return ''
   
    def get_xps_regions(self):
        if self.get_scan_type()=='XPS':
            return str(self.filedata['entry/analyser/region_list'].astype(str))



def save_log(dirpath: Path, col_names: list, outfile: Path):
    """
    create file list of all .nxs files, parse data from each .nxs file and write data to log file
    """
    nxs_list=[file for file in os.listdir(dirpath) if file.endswith('.nxs')]
    nxs_list.sort()
    progress_bar = Bar('Processing', max=len(nxs_list))
    not_implemented_count=0
    with open(outfile,"w",encoding='utf-8') as f:
        for file_count,file in enumerate(nxs_list):
            parser=b07_samplelog_parser(dirpath,file,f)
            if file_count==0:
                parser.save_header_data()
            parser.save_row_data()
            progress_bar.next()
    progress_bar.finish()

    if not_implemented_count>0:
        print(f"WARNING: {not_implemented_count} files were\
               found to have scan_types not implemented in the log creator")
    print(f"saved sample log to :  {str(outfile)}")
    return

def make_out_file(dir_path,out_path):
    """
    parse experiment number from dir_path, and create file name for the specified out_path
    """
    exp_num_matches=re.findall(r"[a-zA-Z]{2}\d{5}-\d",dir_path)
    outfile=out_path/f"{exp_num_matches[0]}_sample_log.tsv"
    return outfile

def main():
    """
    defines function to take in user input arguments and create sample log
    """
    help_str=(
        "Takes in a directory or directory/subfolder path and creates a scan log exporting to csv"
    )
    parser=argparse.ArgumentParser(description=help_str)

    help_str= (
        'enter directory or directory/subfolder path for \
            the experiment you want to create the scan log for'
    )
    parser.add_argument('-dir',"--dir_path",help=help_str)

    help_str= (
        'enter the directory path where you want to save the .csv file'
    )
    parser.add_argument('-out',"--out_path",default=None,help=help_str)

    help_str = (
        "use this argument to specify which columns you would like in your data.\
              Defaults to ['datetime','E_start', 'E_end', 'Endstation','X','Y','Z','Rot','Slits']"
    )
    parser.add_argument("-cols","--col_names",default=['Scan_type','datetime','E_start', \
                        'E_end', 'Endstation','X','Y','Z','Rot','Slits'],help=help_str)


    args=parser.parse_args()
    cols=args.col_names
    dirpath=Path(args.dir_path)
    if args.out_path:
        outpath=Path(args.out_path)
    else:
        outpath=dirpath


    save_log(dirpath,cols,make_out_file(args.dir_path,outpath))

if __name__ == '__main__':
    main()
