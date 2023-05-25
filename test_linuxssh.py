import logging
import os

import pytest

from . import LinuxSSH

# from my_paramiko import LinuxSSH

logger = logging.getLogger(__name__)

REMOTE_DIR = "/home/rkuznecov/tmp/linuxssh"


@pytest.fixture
def terminal():
    linux = LinuxSSH(
        host="impact-pc",
        user="rkuznecov",
    )
    yield linux._get_default_terminal()
    linux.close()


@pytest.fixture
def username():
    return os.getlogin()


def test_os_version(terminal):
    logger.debug(terminal.run("cat /etc/os-release"))


# TODO: Now this test fail always. Set xfail on second calling "run" for unknown_cmd_with_check
@pytest.mark.xfail(reason="This test must be failed")
def test_unknown_command(terminal):
    logger.debug(terminal.run("unknown_cmd_without_check", check=False))
    logger.debug(terminal.run("unknown_cmd_with_check"))


# TODO: Move path to pytest keys
def test_change_directory(terminal, username):
    logger.debug(terminal.run("pwd"))
    terminal.run("cd /home")
    assert f"/home/{username}" in terminal.run("pwd")


def test_pipeline(terminal, username):
    assert username not in terminal.run("cd /home && pwd")


def test_single_quotes(terminal):
    terminal.run("echo 'test single quotes' > deleteme.txt")
    assert "test single quotes" in terminal.run("cat deleteme.txt")


def test_double_quotes(terminal):
    terminal.run('echo "test double quotes" > deleteme.txt')
    assert "test double quotes" in terminal.run("cat deleteme.txt")


def test_show_path(terminal):
    logger.debug(terminal.run("echo $PATH"))


def test_shell_interactivity(terminal):
    assert "non-interactive" in terminal.run(
        "if [[ $- == *i* ]]; then echo interactive; else echo non-interactive; fi"
    )
    assert "non-interactive" in terminal.run("tty -s && echo interactive || echo non-interactive")


def test_interference_env(terminal):
    terminal.run("export UNEXISTED_VAR=test_interference_env")
    assert "test_interference_env" not in terminal.run("echo $TESTVAR")


def test_multiple_cmd(terminal):
    assert "test_multiple_cmd" in terminal.run(
        """
        export TESTVAR=test_multiple_cmd
        echo $TESTVAR
        """
    )


def test_inline_ssh_env(terminal):
    terminal.env = {
        "TEST_INLINE_SSH_ENV": "testval",
    }
    assert "testval" in terminal.run("echo $TEST_INLINE_SSH_ENV")


def test_home_dir(terminal):
    terminal.pre_cmd = f"cd {REMOTE_DIR}"
    assert REMOTE_DIR in terminal.run("pwd")


def test_upload(terminal, tmp_path):
    TEXT = "text for test_upload\n"
    FILENAME = "test_upload.txt"

    file = tmp_path / FILENAME
    file.write_text(TEXT)
    terminal.upload(file, REMOTE_DIR)
    assert TEXT in terminal.run(f"cat {REMOTE_DIR}/{FILENAME}")


def test_download(terminal, tmp_path):
    TEXT = "text for test_download"
    FILENAME = "test_download.txt"

    local_dir = tmp_path
    local_file = local_dir / FILENAME
    terminal.run(f"echo '{TEXT}' > {REMOTE_DIR}/{FILENAME}")
    terminal.download(f"{REMOTE_DIR}/{FILENAME}", f"{local_file}")
    assert TEXT in local_file.read_text()
