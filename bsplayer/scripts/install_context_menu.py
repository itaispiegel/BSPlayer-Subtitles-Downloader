import ctypes
import os
import platform
import re
import string
import sys
import winreg

import click

PYTHONW_EXECUTABLE = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')


def require_windows(func):
    def wrapper(*args, **kwargs):
        if platform.system() != 'Windows':
            sys.exit('ERROR: Can only run on Windows platform')
        return func(*args, **kwargs)

    return wrapper


def require_elevation(func):
    def wrapper(*args, **kwargs):
        if not ctypes.windll.shell32.IsUserAnAdmin():
            sys.exit('ERROR: Must run with admin privileges')
        return func(*args, **kwargs)

    return wrapper


class BSPlayerRegistryInstaller:
    BSPLAYER_KEY_REGEX = re.compile(r"BSPlayerFile\.[A-Z].*?")
    REGISTRY_HIVE = winreg.HKEY_CLASSES_ROOT
    CONTEXT_MENU_TITLE = 'Download Subtitles'
    CONTEXT_MENU_COMMAND_TEMPLATE = string.Template('${python_executable} -m bsplayer.scripts.download_subtitles "%1"')

    def __init__(self, python_executable):
        self.python_executable = python_executable

    @classmethod
    def _winreg_get_subkeys(cls, key):
        i = 0
        result = []
        while True:
            try:
                subkey = winreg.EnumKey(key, i)
                result.append(subkey)
                i += 1
            except WindowsError:
                break
        return result

    @classmethod
    def _is_bsplayer_file_extension_key_name(cls, key):
        return cls.BSPLAYER_KEY_REGEX.fullmatch(key)

    @classmethod
    def _get_bsplayer_subkey_names_for_file_extensions(cls):
        result = []
        with winreg.OpenKeyEx(cls.REGISTRY_HIVE, "") as key:
            for subkey in cls._winreg_get_subkeys(key):
                if cls._is_bsplayer_file_extension_key_name(subkey):
                    result.append(subkey)
                elif len(result) > 0:
                    break
            return result

    @classmethod
    def create_new_command(cls, file_extension, title, command):
        key_path = f'{file_extension}\\shell\\{title}\\command'
        with winreg.CreateKeyEx(cls.REGISTRY_HIVE, key_path) as key:
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, command)

    def install(self):
        bsplayer_subkeys_names = self._get_bsplayer_subkey_names_for_file_extensions()
        for key_name in bsplayer_subkeys_names:
            self.create_new_command(key_name, self.CONTEXT_MENU_TITLE,
                                    self.CONTEXT_MENU_COMMAND_TEMPLATE.substitute(
                                        python_executable=self.python_executable))


@require_windows
@require_elevation
@click.command()
@click.option('-p', '--python-executable', help='Python executable to use', default=PYTHONW_EXECUTABLE)
def install(python_executable):
    installer = BSPlayerRegistryInstaller(python_executable)
    installer.install()
    print('Successfully installed context menu', file=sys.stderr)


if __name__ == '__main__':
    install()
