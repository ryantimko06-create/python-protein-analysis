from data import parse_entry, read_ids


def test_parse_full_entry():
    entry = {
        "rcsb_id": "1ABC",
        "struct": {"title": "50S ribosomal subunit"},
        "exptl": [{"method": "X-RAY DIFFRACTION"}],
        "rcsb_accession_info": {"initial_release_date": "2001-01-01T00:00:00Z"},
        "rcsb_entry_info": {
            "resolution_combined": [2.5],
            "polymer_entity_count": 3,
            "nonpolymer_entity_count": 1,
            "molecular_weight": 1500.5,
        },
    }
    assert parse_entry(entry) == {
        "PDB ID": "1ABC",
        "Title": "50S ribosomal subunit",
        "Experimental Method": "X-RAY DIFFRACTION",
        "Release Date": "2001-01-01T00:00:00Z",
        "Resolution": 2.5,
        "Polymer Entity Count": 3,
        "Non-Polymer Entity Count": 1,
        "Molecular Weight": 1500.5,
    }


def test_parse_empty_entry_uses_defaults():
    assert parse_entry({}) == {
        "PDB ID": "",
        "Title": "",
        "Experimental Method": "",
        "Release Date": "",
        "Resolution": None,
        "Polymer Entity Count": 0,
        "Non-Polymer Entity Count": 0,
        "Molecular Weight": 0.0,
    }


def test_parse_empty_method_list_gives_empty_string():
    assert parse_entry({"exptl": []})["Experimental Method"] == ""


def test_parse_null_counts_become_zero():
    record = parse_entry({"rcsb_entry_info": {"polymer_entity_count": None, "molecular_weight": None}})
    assert record["Polymer Entity Count"] == 0
    assert record["Molecular Weight"] == 0.0


def test_read_ids_skips_blank_lines(tmp_path):
    path = tmp_path / "ids.txt"
    path.write_text("1ABC\n\n  2XYZ  \n\n")
    assert read_ids(path) == ["1ABC", "2XYZ"]
