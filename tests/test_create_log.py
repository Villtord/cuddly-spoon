from B07nxs2txt.scripts.b07_create_log import make_scan_list, parse_scan_range


def test_parse_scan_range():
    outrange = parse_scan_range("[1,5,1]")
    assert outrange == [1, 2, 3, 4, 5]


def test_make_scan_list():
    scan_list_in = [1, 2, 3]
    scan_range = "[4,6,1]"
    assert make_scan_list(scan_list_in, scan_range) == [1, 2, 3, 4, 5, 6]
