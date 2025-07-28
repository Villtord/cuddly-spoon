#!/dls_sw/apps/python/anaconda/1.7.0/64/bin/python
"""
B07-92/B07-264 Script to convert .nxs files to plain text data files
"""

import argparse
import csv
import os
import sys
from argparse import Namespace
from typing import Any

import h5py

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(SCRIPT_DIR), ".."))

from B07nxs2txt._utils import (  # noqa: E402
    GLOBAL_NODE_OLD,
    NUMBER_FORMAT,
    ScanType,
    get_instrument_node,
)

parsed_args: Namespace
filename: str
filedir: str


def output_data(instrument_node):
    global filename

    """Controls the data output according to scan file type"""
    scan_type = classify_scan_type(instrument_node)

    if scan_type == ScanType.XPS:
        print(f"\n{filename} determined to be an XPS scan.")
        region_list = instrument_node["analyser/region_list"]
        print(f"Number of regions found: {region_list.len()}")
        for region in region_list:
            if isinstance(region, bytes):
                region = region.decode("utf-8")
            export_xps_data(instrument_node[region], filename)
        instrument_node.file.close()

    elif scan_type == ScanType.NEXAFS:
        print(f"\n{filename} determined to be a simple NEXAFS scan.")
        export_nexafs_data(instrument_node, filename, None)
        instrument_node.file.close()

    elif scan_type == ScanType.NEXAFS_ANALYSER:
        print(f"\n{filename} determined to be a NEXAFS scan with analyser output.")
        region_list = instrument_node["analyser/region_list"]
        if region_list.len() == 1:
            region_name = region_list[0].decode("utf-8")
            print(f"Region name: {region_name}")
            export_nexafs_data(instrument_node, filename, region_name)
            instrument_node.file.close()
        else:
            print(
                "Number of regions does not equal 1. "
                "Not sure what to do with this file."
            )

    elif scan_type == ScanType.XY_DATA:
        print(f"\n{filename} determined to be an XY_DATA scan.")
        export_xy_data(instrument_node, filename)
        instrument_node.file.close()

    else:
        print(
            f"\nCould not detect type of scan for {filename}. No output file will"
            " be written."
        )


def classify_scan_type(instrument_node):
    """Given an instrument node from a nexus file, attempts to classify
    the type of scan it is. For now, a blunt distinction is used -if the
    analyser is involved, classify as XPS, if not and pgm_energy plus a
    'current' measurement is involved, classify as NEXAFS.
    """

    instrument_keys = instrument_node.keys()
    if "pgm_energy" in instrument_keys and (
        any("ca" in s for s in instrument_keys)
        or (any("femto" in s for s in instrument_keys))
    ):
        # File is some sort of NEXAFS scan
        if "analyser" in instrument_keys:
            return ScanType.NEXAFS_ANALYSER
        else:
            return ScanType.NEXAFS
    elif "analyser" in instrument_keys:
        return ScanType.XPS
    elif (
        ("sm21b_x" in instrument_keys)
        or ("sm21b_y" in instrument_keys)
        or ("sm21b_z" in instrument_keys)
        or ("dummy_a" in instrument_keys)
    ):
        return ScanType.XY_DATA
    else:
        return None


def export_nexafs_data(instrument_node, filename, region_name):
    """Format pgm_energy vs current and trigger writing to
    a file
    """
    title_list = []  # list to store column titles
    data_list = []  # list to store data

    if region_name:
        integrated_data = convert_and_format(region_name, instrument_node)
        title_list.append(region_name)
        data_list.append(integrated_data)

    for item in instrument_node:
        # Adds pgm_energy as well as any scannables with ca/femto in their name
        if (
            item == "pgm_energy"
        ):  # Hacky special case - want this to be the first column
            title_list.insert(0, item)
            formatted_list = convert_and_format(item, instrument_node)
            data_list.insert(0, formatted_list)
        elif ("ca" in item) or ("femto" in item):
            title_list.append(item)
            formatted_list = convert_and_format(item, instrument_node)
            data_list.append(formatted_list)

    if data_list:
        print("Data types found: {}".format(" ".join(title_list)))
        # Combine the datasets into a list of tuples
        zipped = zip(*data_list, strict=False)
        filename = filename.split(".")[0] + "_NEXAFS.dat"
        filename = filename.replace(" ", "_")
        write_data_out(filename, title_list, zipped)
        print(f"Data written to file {filename}")


def convert_and_format(item, instrument_node):
    if isinstance(item, bytes):
        item = item.decode("utf-8")
    path_string = f"{item}/{item}"
    # Convert numpy array to list
    temp_list = instrument_node[path_string][:].flatten().tolist()
    return [NUMBER_FORMAT.format(x) for x in temp_list]


def export_xy_data(instrument_node, filename):
    """Format scannable vs current and trigger writing to a file"""
    title_list = []  # list to store column titles
    data_list = []  # list to store data
    for item in instrument_node:
        if ("sm21b" in item) or (
            "dummy" in item
        ):  # Hacky special case - want this to be the first column
            title_list.insert(0, item)
            formatted_list = convert_and_format(item, instrument_node)
            data_list.insert(0, formatted_list)
        elif ("ca" in item) or ("femto" in item):
            title_list.append(item)
            formatted_list = convert_and_format(item, instrument_node)
            data_list.append(formatted_list)
    if data_list:
        print("Data types found: {}".format(" ".join(title_list)))
        # Combine the datasets into a list of tuples
        zipped = zip(*data_list, strict=False)
        filename = filename.split(".")[0] + "_XY.dat"
        filename = filename.replace(" ", "_")
        write_data_out(filename, title_list, zipped)
        print(f"Data written to file {filename}")


def export_xps_data(region, filename):
    """Format binding_energy vs intensity data and trigger writing to
    a file
    """
    data_list = []
    title_list = ["binding_energy", "intensity"]

    if len(region["binding_energy"].shape) == 2:
        data_list.append(
            [NUMBER_FORMAT.format(x) for x in region["binding_energy"][0][:].tolist()]
        )
    elif len(region["binding_energy"].shape) == 1:
        data_list.append(
            [NUMBER_FORMAT.format(x) for x in region["binding_energy"][:].tolist()]
        )
    data_list.append(
        [NUMBER_FORMAT.format(x) for x in region["spectrum"][0][:].tolist()]
    )

    data_dict = {k: v[0][:].tolist() for k, v in region.items() if "spectrum_" in k}
    for index in range(len(data_dict)):
        spectrum_name = f"spectrum_{index + 1}"
        data_list.append([NUMBER_FORMAT.format(x) for x in data_dict[spectrum_name]])
        title_list.append(spectrum_name)

    zipped = zip(*data_list, strict=False)

    region_name = region.name.split("/")[-1]
    filename = filename.split(".")[0] + "_" + region_name + "_XPS.dat"
    filename = filename.replace(" ", "_")
    write_data_out(filename, title_list, zipped)
    print(f"Data for region {region_name} written to file {filename}")


def write_data_out(filename: str, title_list: list[str], zipped: dict[str, Any]):
    """Writes out the zipped list of data to a file."""
    global filedir
    global parsed_args

    output_path = os.path.join(filedir, filename)
    with open(output_path, "w") as output_file:
        writer = csv.writer(output_file, delimiter="\t")
        if not parsed_args.titles_off:
            writer.writerow(title_list)
        writer.writerows(zipped)


def main():
    global parsed_args, filename, filedir

    filepath = parsed_args.filepath
    filename = filepath.split("/")[-1]
    filedir = filepath.split(filename)[0]

    with h5py.File(filepath, "r") as nexus:
        instrument_node = get_instrument_node(nexus, GLOBAL_NODE_OLD)
        if instrument_node:
            output_data(instrument_node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help=("Full path to nxs file to convert"))
    parser.add_argument(
        "--titles_off", help="Switch OFF column titles", action="store_true"
    )
    parsed_args = parser.parse_args()
    main()
