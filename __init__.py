import logging

import fabric
import invoke

logging.getLogger("paramiko").setLevel(logging.WARNING)
logging.getLogger("invoke").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class CommandError(BaseException):
    pass


class LinuxSSH:
    def __init__(
        self,
        host: str,
        env: dict = dict(),
        user: str = "root",
    ):
        self.host = host
        self.user = user
        self.env = env
        self._pre_cmd = ""

    def _get_default_terminal(self):
        self._connection = fabric.Connection(
            f"{self.user}@{self.host}",
        )
        return self

    def close(self):
        self._connection.close()

    @property
    def pre_cmd(self):
        return self._pre_cmd

    @pre_cmd.setter
    def pre_cmd(self, cmd: str):
        self._pre_cmd = cmd + "\n"

    def run(self, cmd, check=True, timeout=5):
        logger.debug(f"# {cmd}")
        cmd = self.pre_cmd + cmd
        try:
            response = self._connection.run(
                cmd,
                timeout=timeout,
                env=self.env,
            )
        except invoke.exceptions.UnexpectedExit:
            if check:
                raise CommandError(f"Command '{cmd}' returned non-zero exit status")
        else:
            return response.stdout

    def upload(self, src, dest):
        self._connection.put(src, dest)

    def download(self, src, dest):
        self._connection.get(src, dest)
