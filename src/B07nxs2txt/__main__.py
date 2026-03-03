"""Interface for ``python -m B07nxs2txt``."""

import os
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence

import h5py  # Assuming .nxs files are HDF5-compatible

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from B07nxs2txt._utils import (  # noqa: E402
    MAIN_NODE_NEW,
    MAIN_NODE_OLD,
    SCRIPT_NEW,
    SCRIPT_OLD,
)
from B07nxs2txt._version import __version__  # noqa: E402

__all__ = ["main"]

errors: list[str] = []
counter_old: int = 0
counter_new: int = 0
parsed_args: Namespace


def is_main_node_new(file_path: str) -> bool | None:
    """
    Extracts the main node information from the .nxs file.
    Adjust the logic based on the file's structure.
    """
    try:
        main_node = ""
        with h5py.File(file_path, "r") as f:
            # Assuming the main node is stored as an attribute or dataset
            if MAIN_NODE_OLD in f.keys():
                print("File structure is OLD")
                main_node = MAIN_NODE_OLD  # Retrieve the value
            elif MAIN_NODE_NEW in f.keys():
                print("\n File structure is NEW")
                main_node = MAIN_NODE_NEW  # Retrieve the value
            else:
                print(f"No main node found in {file_path}.")
            f.close()
        return main_node == MAIN_NODE_NEW
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def run_script_with_python(file_path: str, script: str, outpath: str):
    """
    Runs the appropriate Python script for the given .nxs file.
    """
    result = None
    try:
        if parsed_args.titles_off:
            command = f"cd {SCRIPT_DIR}; python -m {script} {file_path} -out {outpath} --titles_off"
        else:
            command = f"cd {SCRIPT_DIR}; python -m {script} {file_path} -out {outpath}"
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        if result.stdout == "":
            print("\n WARNING: No output from script - check logs/files")
            errors.append(f"\n WARNING empty result {file_path} \n")
            return
        print(
            f"\n Script executed successfully for {file_path} using \
                Python script {script}. \n Output: \n {result.stdout}"
        )
    except subprocess.CalledProcessError as e:
        print(
            f"\n Script FAILED for {file_path} using Python script {script}. \
            Output: {e.stdout}"
        )
        print(
            f"\n Error while executing script for {file_path} \
            using Python script {script}: {e.stderr}"
        )
        errors.append(f"\n ERROR {file_path} : {e.stderr} \n")


def process_file(file_path):
    global counter_old
    global counter_new

    
    outpath=parsed_args.out_path
    print("\n" + "#" * 50)
    print(f"Processing file: {file_path}")
	# Determine the Python version based on the main node
    main_node_new = is_main_node_new(file_path)
    if main_node_new is None:
        print(f"Skipping {file_path} due to missing main node.")
        return
    if main_node_new:
        run_script_with_python(file_path, SCRIPT_NEW, outpath)
        counter_new += 1
    else:
        run_script_with_python(file_path, SCRIPT_OLD, outpath)
        counter_old += 1

def parse_scan_range(scan_range):
    s = scan_range.strip("[]")
    start, stop, step = map(int, s.split(","))
    return list(range(start, stop + 1, step))


def make_scan_list(scan_list_in, scan_range):
    if len(scan_range) > 0:
        add_scans = parse_scan_range(scan_range)
        scan_list_in.extend(add_scans)
    return scan_list_in

def process_folder():
    """
    Processes all .nxs files in the folder.
    """
    nxs_files: list[str]

    if not os.path.isdir(parsed_args.path):
        print(f"The provided path {parsed_args.path} is not a valid folder.")
        return
    # Get all .nxs files
    scan_list = make_scan_list(parsed_args.scan_list, parsed_args.scan_range)
    nxs_list_all = [file for file in os.listdir(parsed_args.path) if file.endswith(".nxs")]
    if len(scan_list) == 0:
        nxs_files = nxs_list_all
    else:
        nxs_files = [
            file for file in nxs_list_all if any(str(num) in file for num in scan_list)
        ]

    if not nxs_files:
        print(f"No .nxs files found in the folder {parsed_args.path}.")
        return
    for nxs_file in nxs_files:	
        print(os.path.abspath(parsed_args.path))
        file_path = os.path.join(os.path.abspath(parsed_args.path), nxs_file)
        process_file(file_path)


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    global parsed_args

    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )
    parser.add_argument("path", help=("Full path to nxs file or folder to convert files"))
    parser.add_argument(
        "--titles_off", help="Switch OFF column titles", action="store_true"
    )
    
    help_str = "enter the directory path where you want to save the converted data"
    parser.add_argument("-out", "--out_path", default=None, help=help_str)

    help_str = "Separate scan numbers to be mapped into the log without brackets e.g 441124 441128"
    parser.add_argument("-sl", "--scan_list", nargs="+", type=int, help=help_str,default=[])

    help_str = "Evenly spaced range of scans to be added to the log in the format [start,stop,step]"
    parser.add_argument("-sr", "--scan_range", help=help_str, default=[])

    parsed_args = parser.parse_args()

    if parsed_args.out_path is None:
        parsed_args.out_path =  parsed_args.path
	# do conversion
    if os.path.isfile(parsed_args.path):
        process_file(parsed_args.path)
    else:
        process_folder()

    print(f"NUMBER OF PROCESSED NEW FILES: {counter_new} \n")
    print(f"NUMBER OF PROCESSED OLD FILES: {counter_old} \n")
    print("ALL ERRORS: " + "\n")
    print(errors)


if __name__ == "__main__":
    main()
