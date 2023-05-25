import logging

import paramiko

logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class LinuxSSH:
    def __init__(self, host, user="root"):
        self.host = host
        self.user = user

    def _get_default_terminal(self):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            hostname=self.host,
            username=self.user,
        )
        return self

    def run(self, cmd: str, check: bool = True, timeout=5):
        logger.debug(f"# {cmd}")
        _, stdout_, stderr_ = self._client.exec_command(cmd, timeout=timeout)
        response = "".join(stdout_.readlines())

        if not check:
            return response

        code = stdout_.channel.recv_exit_status()
        if code:
            raise paramiko.SSHException(
                f"Command '{cmd}' returned non-zero exit status {code}. \
                    \nstderr:\n{''.join(stderr_.readlines())}"
            )
        return response
