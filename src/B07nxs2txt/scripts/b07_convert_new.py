"""
Script to convert .nxs file to plain text data files
Requires python 3!
"""

import argparse
import csv
import os
import sys
from argparse import Namespace
from typing import Any

import h5py
from h5py._hl.files import File

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(os.path.dirname(SCRIPT_DIR), ".."))

from B07nxs2txt._utils import (  # noqa: E402
    CLASSIFICATIION_NODE_NEW,
    GLOBAL_NODE_NEW,
    ScanType,
    get_classification_node,
    get_instrument_node,
)

NUMBER_FORMAT = "{0:.8g}"
parsed_args: Namespace
filename: str
filedir: str


def output_data(instrument_node: File, classification_node: list[str] | None):
    """Controls the data output according to scan file type"""
    global filename
    scan_type = classify_scan_type(classification_node)

    if scan_type == ScanType.XPS:
        print(f"\n{filename} determined to be an XPS scan.")
        region_list = instrument_node["analyser/region_list"]
        print(f"\n region list {region_list[:]}")
        print(f"Number of regions found: {len(region_list[0, :])}")
        for region in region_list[0, :]:
            print(f"\n Region {region.decode('utf-8')}")
            export_xps_data(instrument_node[region.decode("utf-8")], filename)
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


def classify_scan_type(classification_node: list[str] | None) -> ScanType | None:
    """Given an instrument node from a nexus file, attempts to classify
    the type of scan it is. For now, a blunt distinction is used -if the
    analyser is involved, classify as XPS, if not and pgm_energy plus a
    'current' measurement is involved, classify as NEXAFS.
    """
    instrument_keys: list[str]

    if classification_node is None:
        return None

    instrument_keys = [i.decode("utf-8") for i in classification_node]

    # print (f"classification values {instrument_keys}")
    if any(s.startswith("pgm_energy") for s in instrument_keys) and (
        any(s.startswith("ca") for s in instrument_keys)
        or (any(s.startswith("femto") for s in instrument_keys))
    ):
        # File is some sort of NEXAFS scan
        if any(s.startswith("analyser") for s in instrument_keys):
            return ScanType.NEXAFS_ANALYSER
        else:
            return ScanType.NEXAFS
    elif any(s.startswith("analyser") for s in instrument_keys):
        return ScanType.XPS
    elif (
        any(s.startswith("sm21b_x") for s in instrument_keys)
        or any(s.startswith("sm21b_y") for s in instrument_keys)
        or any(s.startswith("sm21b_z") for s in instrument_keys)
        or any(s.startswith("dummy_a") for s in instrument_keys)
    ):
        return ScanType.XY_DATA
    else:
        return None


def export_nexafs_data(instrument_node: list[str], filename: str, region_name: str):
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
            formatted_list = convert_and_format(item, instrument_node)
            if formatted_list != []:
                title_list.insert(0, item)
                data_list.insert(0, formatted_list)
        elif ("ca" in item) or ("femto" in item):
            formatted_list = convert_and_format(item, instrument_node)
            if formatted_list != []:
                title_list.append(item)
                data_list.append(formatted_list)

    if data_list:
        print("Data types found: {}".format(" ".join(title_list)))
        # Combine the datasets into a list of tuples
        zipped = zip(*data_list, strict=False)
        filename = filename.split(".")[0] + "_NEXAFS.dat"
        filename = filename.replace(" ", "_")
        write_data_out(filename, title_list, zipped)
        print(f"Data written to file {filename}")


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


def export_xps_data(region, filename: str):
    """Format binding_energy vs intensity data and trigger writing to
    a file
    """

    data_list = []
    title_list = ["binding_energy", "intensity"]

    if region["binding_energy"].shape[0] == 0:
        print("Empty binding energy dataset - skipping file")
        return

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

    data_dict = {
        k: v[0][:].tolist()
        for k, v in region.items()
        if (("spectrum_" in k) and (v.shape[0] > 0))
    }
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


def convert_and_format(item, instrument_node):
    if "value" in instrument_node[item].keys():
        path_string = f"{item}/value"
    elif item in instrument_node[item].keys():
        path_string = f"{item}/{item}"
    else:
        return []

    # print ("Path stirng {}".format(path_string))
    # print (list(instrument_node[item]))

    if instrument_node[path_string].ndim == 0:
        return []
    elif instrument_node[path_string].ndim == 1:
        object = instrument_node[path_string]
        return [NUMBER_FORMAT.format(object[i]) for i in range(object.len())]


def write_data_out(filename: str, title_list: list[str], zipped: dict[str, Any]):
    """Writes out the zipped list of data to a file."""
    global filedir
    global parsed_args

    output_path = os.path.join(filedir, filename)
    with open(output_path, "w") as output_file:
        writer = csv.writer(output_file, delimiter="\t")
        if parsed_args.titles_on:
            writer.writerow(title_list)
        writer.writerows(zipped)


def main():
    global parsed_args, filename, filedir

    filepath = parsed_args.filepath
    filename = filepath.split("/")[-1]
    filedir = filepath.split(filename)[0]

    with h5py.File(filepath, "r") as nexus:
        instrument_node = get_instrument_node(nexus, GLOBAL_NODE_NEW)
        classification_node = get_classification_node(nexus, CLASSIFICATIION_NODE_NEW)
        if instrument_node:
            output_data(instrument_node, classification_node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help=("Full path to nxs file to convert"))
    parser.add_argument(
        "--titles_on", help="Switch on column titles", action="store_true"
    )
    parsed_args = parser.parse_args()
    main()
