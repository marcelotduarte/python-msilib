"""Test suite for the code in msilib."""

import os

import pytest

msilib = pytest.importorskip("msilib", reason="Windows tests")
schema = pytest.importorskip("msilib.schema", reason="Windows tests")
sequence = pytest.importorskip("msilib.sequence", reason="Windows tests")


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "test.msi"
    db = msilib.init_database(
        path.as_posix(), schema, "Python Tests", "product_code", "1.0", "PSF"
    )
    yield db
    db.Close()


def test_view_fetch_returns_none(db) -> None:
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


def test_view_non_ascii(db) -> None:
    view = db.OpenView("SELECT 'ß-розпад' FROM Property")
    view.Execute(None)
    record = view.Fetch()
    assert record.GetString(1) == "ß-розпад"
    view.Close()


def test_summaryinfo_getproperty_issue1104(db) -> None:
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


def test_database_open_failed() -> None:
    with pytest.raises(msilib.MSIError) as exc:
        msilib.OpenDatabase("non-existent.msi", msilib.MSIDBOPEN_READONLY)
    assert exc.match("open failed")


def test_database_create_failed(tmp_path) -> None:
    with pytest.raises(msilib.MSIError) as exc:
        msilib.OpenDatabase(tmp_path.as_posix(), msilib.MSIDBOPEN_CREATE)
    assert exc.match("create failed")


def test_get_property_vt_empty(db) -> None:
    summary = db.GetSummaryInformation(0)
    assert summary.GetProperty(msilib.PID_SECURITY) is None


def test_directory_start_component_keyfile(db, tmp_path) -> None:
    try:
        feature = msilib.Feature(db, 0, "Feature", "A feature", "Python")
        cab = msilib.CAB("CAB")
        directory = msilib.Directory(
            db, cab, None, tmp_path, "TARGETDIR", "SourceDir", 0
        )
        directory.start_component(None, feature, None, "keyfile")
    finally:
        msilib._directories.clear()  # noqa: SLF001


def test_large_package(db, tmp_path) -> None:
    root_dir = tmp_path / "root"
    root_dir.mkdir()
    data_dir = root_dir / "data"
    data_dir.mkdir()
    for i in range(33000):
        file = data_dir / f"{i:05}.dat"
        file.write_text(f"data {i}")
    msilib.add_tables(db, sequence)
    try:
        cab = msilib.CAB("distfiles")
        feature = msilib.Feature(
            db,
            "default",
            "Default Feature",
            "Everything",
            1,
            directory="TARGETDIR",
        )
        feature.set_current()
        root = msilib.Directory(
            db, cab, None, root_dir, "TARGETDIR", "SourceDir"
        )
        db.Commit()
        todo = [root]
        while todo:
            directory = todo.pop()
            for file in os.listdir(directory.absolute):
                if os.path.isdir(os.path.join(directory.absolute, file)):
                    sfile = directory.make_short(file)
                    new_dir = msilib.Directory(
                        db, cab, directory, file, file, f"{sfile}|{file}"
                    )
                    todo.append(new_dir)
                else:
                    directory.add_file(file)
        cab.commit(db)
    finally:
        msilib._directories.clear()  # noqa: SLF001


def test_getproperty_uninitialized_var(db) -> None:
    si = db.GetSummaryInformation(0)
    with pytest.raises(msilib.MSIError):
        si.GetProperty(-1)


def test_FCICreate(tmp_path) -> None:
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


def test_make_id_no_change_required() -> None:
    assert msilib.make_id("short") == "short"
    assert msilib.make_id("nochangerequired") == "nochangerequired"
    assert msilib.make_id("one.dot") == "one.dot"
    assert msilib.make_id("_") == "_"
    assert msilib.make_id("a") == "a"
    # assert msilib.make_id("") == ""  # noqa: ERA001


def test_make_id_invalid_first_char() -> None:
    assert msilib.make_id("9.short") == "_9.short"
    assert msilib.make_id(".short") == "_.short"


def test_make_id_invalid_any_char() -> None:
    assert msilib.make_id(".s\x82ort") == "_.s_ort"
    assert msilib.make_id(".s\x82o?*+rt") == "_.s_o___rt"
