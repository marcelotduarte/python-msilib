"""Test suite for the code in msilib."""

import msilib
import msilib.schema

import pytest


@pytest.fixture
def db(tmp_path):  # -> msilib.Database
    path = tmp_path / "test.msi"
    db = msilib.init_database(
        str(path), msilib.schema, "Python Tests", "product_code", "1.0", "PSF"
    )
    yield db
    db.Close()


def test_view_fetch_returns_none(db):
    properties = []
    view = db.OpenView("SELECT Property, Value FROM Property")
    view.Execute(None)
    while True:
        record = view.Fetch()
        if record is None:
            break
        properties.append(record.GetString(1))
    view.Close()
    assert properties == [
        "ProductName",
        "ProductCode",
        "ProductVersion",
        "Manufacturer",
        "ProductLanguage",
    ]


def test_view_non_ascii(db):
    view = db.OpenView("SELECT 'ß-розпад' FROM Property")
    view.Execute(None)
    record = view.Fetch()
    assert record.GetString(1) == "ß-розпад"
    view.Close()


def test_summaryinfo_getproperty_issue1104(db):
    try:
        sum_info = db.GetSummaryInformation(99)
        title = sum_info.GetProperty(msilib.PID_TITLE)
        assert title == b"Installation Database"

        sum_info.SetProperty(msilib.PID_TITLE, "a" * 999)
        title = sum_info.GetProperty(msilib.PID_TITLE)
        assert title == b"a" * 999

        sum_info.SetProperty(msilib.PID_TITLE, "a" * 1000)
        title = sum_info.GetProperty(msilib.PID_TITLE)
        assert title == b"a" * 1000

        sum_info.SetProperty(msilib.PID_TITLE, "a" * 1001)
        title = sum_info.GetProperty(msilib.PID_TITLE)
        assert title == b"a" * 1001
    finally:
        db = None
        sum_info = None


def test_database_open_failed():
    with pytest.raises(msilib.MSIError) as exc:
        msilib.OpenDatabase("non-existent.msi", msilib.MSIDBOPEN_READONLY)
    assert exc.match("open failed")


def test_database_create_failed(tmp_path):
    with pytest.raises(msilib.MSIError) as exc:
        msilib.OpenDatabase(tmp_path.as_posix(), msilib.MSIDBOPEN_CREATE)
    assert exc.match("create failed")


def test_get_property_vt_empty(db):
    summary = db.GetSummaryInformation(0)
    assert summary.GetProperty(msilib.PID_SECURITY) is None


def test_directory_start_component_keyfile(db, tmp_path):
    try:
        feature = msilib.Feature(db, 0, "Feature", "A feature", "Python")
        cab = msilib.CAB("CAB")
        dir = msilib.Directory(
            db, cab, None, tmp_path, "TARGETDIR", "SourceDir", 0
        )
        dir.start_component(None, feature, None, "keyfile")
    finally:
        msilib._directories.clear


def test_getproperty_uninitialized_var(db):
    si = db.GetSummaryInformation(0)
    with pytest.raises(msilib.MSIError):
        si.GetProperty(-1)


def test_FCICreate(tmp_path):
    filepath = tmp_path / "test.txt"
    cabpath = tmp_path / "test.cab"
    filepath.touch()
    msilib.FCICreate(cabpath.as_posix(), [(filepath.as_posix(), "test.txt")])
    assert cabpath.is_file()


# http://msdn.microsoft.com/en-us/library/aa369212(v=vs.85).aspx
"""The Identifier data type is a text string. Identifiers may contain the
ASCII characters A-Z (a-z), digits, underscores (_), or periods (.).
However, every identifier must begin with either a letter or an
underscore.
"""


def test_make_id_no_change_required():
    assert msilib.make_id("short") == "short"
    assert msilib.make_id("nochangerequired") == "nochangerequired"
    assert msilib.make_id("one.dot") == "one.dot"
    assert msilib.make_id("_") == "_"
    assert msilib.make_id("a") == "a"
    # assert msilib.make_id("") == ""


def test_make_id_invalid_first_char():
    assert msilib.make_id("9.short") == "_9.short"
    assert msilib.make_id(".short") == "_.short"


def test_make_id_invalid_any_char():
    assert msilib.make_id(".s\x82ort") == "_.s_ort"
    assert msilib.make_id(".s\x82o?*+rt") == "_.s_o___rt"
