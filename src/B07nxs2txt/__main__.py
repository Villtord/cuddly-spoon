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


def run_script_with_python(file_path: str, script: str):
    """
    Runs the appropriate Python script for the given .nxs file.
    """
    result = None
    try:
        if parsed_args.titles_off:
            command = f"cd {SCRIPT_DIR}; python -m {script} {file_path} --titles_off"
        else:
            command = f"cd {SCRIPT_DIR}; python -m {script} {file_path}"
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


def process_folder():
    """
    Processes all .nxs files in the folder.
    """
    global counter_old
    global counter_new
    nxs_files: list[str]

    if not os.path.isdir(parsed_args.folderpath):
        print(f"The provided path {parsed_args.folderpath} is not a valid folder.")
        return
    # Get all .nxs files
    nxs_files = [f for f in os.listdir(parsed_args.folderpath) if f.endswith(".nxs")]
    if not nxs_files:
        print(f"No .nxs files found in the folder {parsed_args.folderpath}.")
        return
    for nxs_file in nxs_files:
        print(os.path.abspath(parsed_args.folderpath))
        file_path = os.path.join(os.path.abspath(parsed_args.folderpath), nxs_file)
        print("\n" + "#" * 50)
        print(f"Processing file: {file_path}")
        # Determine the Python version based on the main node
        main_node_new = is_main_node_new(file_path)
        if main_node_new is None:
            print(f"Skipping {file_path} due to missing main node.")
            continue
        if main_node_new:
            run_script_with_python(file_path, SCRIPT_NEW)
            counter_new += 1
        else:
            run_script_with_python(file_path, SCRIPT_OLD)
            counter_old += 1


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
    parser.add_argument("folderpath", help=("Full path to nxs folder to convert files"))
    parser.add_argument(
        "--titles_off", help="Switch OFF column titles", action="store_true"
    )

    parsed_args = parser.parse_args()

    # do conversion
    process_folder()

    print(f"NUMBER OF PROCESSED NEW FILES: {counter_new} \n")
    print(f"NUMBER OF PROCESSED OLD FILES: {counter_old} \n")
    print("ALL ERRORS: " + "\n")
    print(errors)


if __name__ == "__main__":
    main()
