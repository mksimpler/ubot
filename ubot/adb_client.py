from enum import Enum
import subprocess
from ppadb.client import Client as AdbClient

from ubot import logger


class ADBServerState(Enum):
    CLOSED = 0
    OPENED = 1


class ADBClient:

    def __init__(self, host=None, port=None, serial=None):
        self.state = ADBServerState.CLOSED
        self.device = None

        self._host = host if host is not None else "127.0.0.1"
        self._port = port if port is not None else 5037
        self._serial = serial

    def start_server(self):
        """
        Start ADB server
        """
        try:
            _adb_kill_server()
            _adb_start_server()
            client = AdbClient(host=self._host, port=self._port)

            if (self._serial or "") == "":
                devices = client.devices()
                if len(devices) == 1:
                    self.device = devices[0]
                elif len(devices) > 1:
                    raise DeviceNotProvidedException()
                else:
                    raise DeviceNotFoundException()
            else:
                self.device = client.device(self._serial)

            self.state = ADBServerState.OPENED
            logger.debug("ADB server started successfully.")
        except Exception as ex:
            _adb_kill_server()
            logger.debug("ADB server has failed to start.")
            self.state = ADBServerState.CLOSED

            raise ex

    def stop_server(self):
        """
        Stop ADB server
        """
        _adb_kill_server()
        logger.debug("ADB server has been shut down.")

        self.state = ADBServerState.CLOSED
        self.device = None

    def exec_out(self, command):
        """
        Executes the command via exec-out

        Parameter
        ---------
        command
            string
            Command to execute.

        Returns
        -------
        tuple
            A tuple containing stdoutdata and stderrdata
        """
        if self.state == ADBServerState.OPENED:
            cmd = [_ADB_COMMAND, self.device, 'exec-out'] + command.split(' ')
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            return process.communicate()[0]

    def shell(self, command):
        """
        Executes the command via adb shell

        Parameter
        ---------
        command
            string
            Command to execute
        """
        if self.state == ADBServerState.OPENED:
            self.device.shell(command)

    @property
    def screencap(self):
        """
        Capture emulator screen

        Returns
        -------
        binary
            Screen image in binary data
        """
        if self.state == ADBServerState.OPENED:
            return self.device.screencap()

    @property
    def screensize(self):
        """
        Get device's screen size

        Returns
        -------
        tuple(int, int)
            Size of device in order width, height
        """
        if self.state == ADBServerState.OPENED:
            screen = self.device.wm_size()
            return screen.width, screen.height


class ServerNotStartedException(Exception):
    pass


class DeviceNotProvidedException(Exception):
    def __init__(self):
        super().__init__("There are more than one device")


class DeviceNotFoundException(Exception):
    def __init__(self):
        super().__init__("No devices has found")


_ADB_COMMAND = "adb"


def _adb_start_server():
    """
    Starts the ADB server
    """
    subprocess.run(f"{_ADB_COMMAND} start-server", capture_output=True, check=True)


def _adb_kill_server():
    """
    Kills the ADB server
    """
    subprocess.run(f"{_ADB_COMMAND} kill-server", capture_output=True, check=True)
