from enum import Enum

from h5py._hl.files import File

MAIN_NODE_NEW = "/entry"
MAIN_NODE_OLD = "/entry1"
GLOBAL_NODE_OLD = "/entry1/instrument"
GLOBAL_NODE_NEW = "/entry/instrument"
CLASSIFICATIION_NODE_NEW = "/entry/diamond_scan/scan_fields"

SCRIPT_OLD = "scripts.b07_convert_old"
SCRIPT_NEW = "scripts.b07_convert_new"

PGM_NAMES = ("pgm_energy", "pgm_cff")
XY_SCAN_SCANNABLES_NAMES = ("sm21b_x", "sm21b_y", "sm21b_z", "dummy_a")

NUMBER_FORMAT = "{0:.8g}"


class ScanType(Enum):
    """An enum to represent scan types"""

    XPS = 0
    NEXAFS = 1  # Simple NEXAFS with just photon energy vs current
    NEXAFS_ANALYSER = 2  # NEXAFS using the analyser in addition to current
    XY_DATA = 3  # dummy scans or sample manipulator scans


def get_instrument_node(global_node: File, node_path: str) -> File | None:
    return global_node[node_path]


def get_classification_node(global_node: File, node_path: str) -> list[str] | None:
    return global_node[node_path]
