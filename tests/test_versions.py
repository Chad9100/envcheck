import json

import pytest

from envcheck.versions import check_versions, parse_version, satisfies


def statuses(results):
    return [r.status for r in results]


@pytest.mark.parametrize(
    "have,spec,expected",
    [
        ((3, 12, 1), ">=3.11", True),
        ((3, 10, 0), ">=3.11", False),
        ((3, 12, 1), ">=3.11,<3.13", True),
        ((3, 13, 0), ">=3.11,<3.13", False),
        ((3, 11, 4), "3.11", True),
        ((3, 12, 0), "3.11", False),
        ((18, 5, 0), "^18", True),
        ((20, 0, 0), "^18", False),
        ((20, 1, 0), ">=18 || ^16", True),
        ((3, 11, 9), "~=3.11.2", True),
        ((3, 12, 0), "~=3.11.2", False),
        ((3, 14, 0), "~=3.11", True),
        ((20, 0, 0), ">= 18", True),
        ((3, 9, 0), "!=3.9", False),
        ((1, 0, 0), "*", True),
    ],
)
def test_satisfies(have, spec, expected):
    assert satisfies(have, spec) is expected


def test_satisfies_garbage_returns_none():
    assert satisfies((3, 12, 0), "banana") is None


def test_parse_version():
    assert parse_version("v18.17.1") == (18, 17, 1)
    assert parse_version("3.11") == (3, 11)
    assert parse_version("lts/*") is None


def test_no_files(tmp_path):
    r = check_versions(tmp_path)
    assert statuses(r) == ["PASS"]


def test_python_version_file_pass_and_fail(tmp_path):
    (tmp_path / ".python-version").write_text("3.11\n")
    assert statuses(check_versions(tmp_path, python_version=(3, 11, 5))) == ["PASS"]
    assert statuses(check_versions(tmp_path, python_version=(3, 12, 0))) == ["FAIL"]


def test_python_version_file_garbage_warns(tmp_path):
    (tmp_path / ".python-version").write_text("system\n")
    assert statuses(check_versions(tmp_path)) == ["WARN"]


def test_requires_python(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\nrequires-python=">=3.8"\n')
    assert statuses(check_versions(tmp_path, python_version=(3, 12, 0))) == ["PASS"]
    (tmp_path / "pyproject.toml").write_text('[project]\nname="x"\nrequires-python=">=4.0"\n')
    assert statuses(check_versions(tmp_path, python_version=(3, 12, 0))) == ["FAIL"]


def test_nvmrc(tmp_path):
    (tmp_path / ".nvmrc").write_text("v18.0.0\n")
    assert statuses(check_versions(tmp_path, node_version=(18, 0, 0))) == ["PASS"]
    assert statuses(check_versions(tmp_path, node_version=(16, 0, 0))) == ["FAIL"]


def test_nvmrc_node_missing(tmp_path):
    (tmp_path / ".nvmrc").write_text("18\n")
    r = check_versions(tmp_path, node_version=None)
    assert statuses(r) == ["FAIL"]
    assert "not installed" in r[0].message


def test_nvmrc_alias_warns(tmp_path):
    (tmp_path / ".nvmrc").write_text("lts/*\n")
    assert statuses(check_versions(tmp_path, node_version=(20, 0, 0))) == ["WARN"]


def test_package_json_engines(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"engines": {"node": ">=18"}}))
    assert statuses(check_versions(tmp_path, node_version=(20, 1, 0))) == ["PASS"]
    assert statuses(check_versions(tmp_path, node_version=(14, 0, 0))) == ["FAIL"]


def test_invalid_package_json_ignored(tmp_path):
    (tmp_path / "package.json").write_text("{not json")
    assert statuses(check_versions(tmp_path)) == ["PASS"]
