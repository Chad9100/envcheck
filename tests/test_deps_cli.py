import json

import pytest

from envcheck.cli import main
from envcheck.deps import check_deps, is_installed, requirement_name


@pytest.mark.parametrize(
    "line,name",
    [
        ("requests>=2.0", "requests"),
        ("  pytest==8.0  # dev", "pytest"),
        ("flask[async]~=3.0", "flask"),
        ("# comment", None),
        ("", None),
        ("-r other.txt", None),
        ("git+https://example.invalid/x.git", None),
    ],
)
def test_requirement_name(line, name):
    assert requirement_name(line) == name


def test_is_installed():
    assert is_installed("pytest")
    assert not is_installed("definitely-not-a-real-pkg-xyz")


def test_requirements_txt_pass_and_fail(tmp_path):
    (tmp_path / "requirements.txt").write_text("pytest\n")
    assert check_deps(tmp_path)[0].status == "PASS"
    (tmp_path / "requirements.txt").write_text("pytest\nnot-a-real-pkg-xyz\n")
    r = check_deps(tmp_path)
    assert r[0].status == "FAIL"
    assert "not-a-real-pkg-xyz" in r[0].message


def test_pyproject_dependencies(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname="x"\nversion="0"\ndependencies=["pytest>=7","not-a-real-pkg-xyz"]\n'
    )
    r = check_deps(tmp_path)
    assert r[0].status == "FAIL"


def test_package_json_node_modules(tmp_path):
    (tmp_path / "package.json").write_text(json.dumps({"dependencies": {"left-pad": "1"}}))
    assert check_deps(tmp_path)[0].status == "FAIL"
    (tmp_path / "node_modules").mkdir()
    assert check_deps(tmp_path)[0].status == "PASS"


def test_package_json_no_deps_warns(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    assert check_deps(tmp_path)[0].status == "WARN"


def test_no_dep_files(tmp_path):
    assert check_deps(tmp_path)[0].status == "PASS"


def test_cli_empty_folder_ok(tmp_path, capsys):
    assert main([str(tmp_path)]) == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_fail_exit_code(tmp_path, capsys):
    (tmp_path / ".env.example").write_text("A=\n")
    assert main([str(tmp_path)]) == 1
    assert "FAIL" in capsys.readouterr().out


def test_cli_json(tmp_path, capsys):
    (tmp_path / ".env.example").write_text("A=\n")
    code = main([str(tmp_path), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    assert code == 1
    assert data["ok"] is False
    assert any(r["status"] == "FAIL" for r in data["results"])


def test_cli_json_ok(tmp_path, capsys):
    main([str(tmp_path), "--format", "json"])
    assert json.loads(capsys.readouterr().out)["ok"] is True


def test_cli_bad_folder(tmp_path, capsys):
    assert main([str(tmp_path / "nope")]) == 2


def test_cli_does_not_leak_env_values(tmp_path, capsys):
    (tmp_path / ".env.example").write_text("A=\n")
    (tmp_path / ".env").write_text("A=fake-secret-123\nB=other-fake-456\n")
    main([str(tmp_path)])
    main([str(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    assert "fake-secret-123" not in out
    assert "other-fake-456" not in out


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0
    assert "envcheck" in capsys.readouterr().out
