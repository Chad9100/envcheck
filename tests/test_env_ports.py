import socket

from envcheck.envfile import check_env, parse_keys
from envcheck.ports import check_ports, port_is_free


def test_parse_keys_ignores_comments_and_values(tmp_path):
    f = tmp_path / ".env.example"
    f.write_text("# comment\n\nAPI_URL=http://x\nexport TOKEN=\n  SPACED = 1\nnoequals\n")
    assert parse_keys(f) == {"API_URL", "TOKEN", "SPACED"}


def test_env_no_example_skips(tmp_path):
    r = check_env(tmp_path)
    assert [x.status for x in r] == ["PASS"]


def test_env_missing_file_fails(tmp_path):
    (tmp_path / ".env.example").write_text("A=1\n")
    r = check_env(tmp_path)
    assert r[0].status == "FAIL"


def test_env_all_present(tmp_path):
    (tmp_path / ".env.example").write_text("A=\nB=\n")
    (tmp_path / ".env").write_text("B=x\nA=y\n")
    r = check_env(tmp_path)
    assert [x.status for x in r] == ["PASS"]


def test_env_missing_and_extra(tmp_path):
    (tmp_path / ".env.example").write_text("A=\nB=\n")
    (tmp_path / ".env").write_text("A=1\nC=2\n")
    r = check_env(tmp_path)
    assert [x.status for x in r] == ["FAIL", "WARN"]
    assert "B" in r[0].message
    assert "C" in r[1].message


def test_env_never_prints_values(tmp_path):
    (tmp_path / ".env.example").write_text("SECRET_KEY=\nOTHER=\n")
    (tmp_path / ".env").write_text("SECRET_KEY=hunter2-fake\nEXTRA=zzz-fake-value\n")
    text = " ".join(x.message for x in check_env(tmp_path))
    assert "hunter2-fake" not in text
    assert "zzz-fake-value" not in text


def test_env_bom_file(tmp_path):
    (tmp_path / ".env.example").write_bytes(b"\xef\xbb\xbfA=\n")
    (tmp_path / ".env").write_text("A=1\n")
    assert check_env(tmp_path)[0].status == "PASS"


def test_port_free_and_busy():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        busy = s.getsockname()[1]
        assert port_is_free(busy) is False
    assert port_is_free(busy) is True


def test_port_out_of_range():
    assert port_is_free(0) is False
    assert port_is_free(70000) is False


def test_ports_none_configured(tmp_path):
    r = check_ports(tmp_path)
    assert r[0].status == "PASS"


def test_ports_from_envcheck_toml(tmp_path):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        busy = s.getsockname()[1]
        (tmp_path / "envcheck.toml").write_text(f"ports = [{busy}]\n")
        r = check_ports(tmp_path)
        assert [x.status for x in r] == ["FAIL"]


def test_ports_from_pyproject_section(tmp_path):
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        free = s.getsockname()[1]
    (tmp_path / "pyproject.toml").write_text(f"[tool.envcheck]\nports = [{free}]\n")
    r = check_ports(tmp_path)
    assert [x.status for x in r] == ["PASS"]


def test_envcheck_toml_overrides_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool.envcheck]\nports = [1]\n")
    (tmp_path / "envcheck.toml").write_text("ports = []\n")
    assert check_ports(tmp_path)[0].message.startswith("no ports")


def test_invalid_toml_ignored(tmp_path):
    (tmp_path / "envcheck.toml").write_text("ports = [")
    assert check_ports(tmp_path)[0].status == "PASS"
