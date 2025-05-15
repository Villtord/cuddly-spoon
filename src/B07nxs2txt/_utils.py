from enum import Enum

from h5py._hl.files import File

MAIN_NODE_NEW = "/entry"
MAIN_NODE_OLD = "/entry1"
GLOBAL_NODE_OLD = "/entry1/instrument"
GLOBAL_NODE_NEW = "/entry/instrument"
CLASSIFICATIION_NODE_NEW = "/entry/diamond_scan/scan_fields"

# dev config
WORKSPACE = "/workspaces/nxs2txtB07/src/B07nxs2txt/"
## main config
# WORKSPACE = "/dls_sw/b07/scripts/Data_Handling/universal_script/"

SCRIPT_OLD = WORKSPACE + "b07_convert_old.py"
SCRIPT_NEW = WORKSPACE + "b07_convert_new.py"


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
