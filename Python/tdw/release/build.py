from requests import get, head
from typing import Tuple
from subprocess import call
from platform import system
from pathlib import Path
from zipfile import ZipFile
from distutils import dir_util
import tarfile
from tdw.version import __version__
from tdw.backend.platforms import SYSTEM_TO_RELEASE


class Build:
    """
    Various helper functions for TDW builds.
    """

    BUILD_ROOT_DIR = Path.home().joinpath(f"tdw_build")

    @staticmethod
    def get_url(version: str = __version__) -> Tuple[str, bool]:
        """
        :param version: The version of the build. Default = the installed version of TDW.

        :return: The URL of the build release matching the version and the OS of this machine, True if the URL exists.
        """

        url = f"https://github.com/threedworld-mit/tdw/releases/download/{version}/" \
              f"{SYSTEM_TO_RELEASE[system()]}"
        if system() == "Windows":
            url += ".zip"
        else:
            url += ".tar.gz"
        # Check if the URL exists.
        if head(url).status_code != 302:
            print(f"Release not found: {url}")
            release_exists = False
        else:
            release_exists = True
        return url, release_exists

    @staticmethod
    def download(version: str = __version__, v_prefix: bool = True) -> bool:
        """
        Download the release corresponding to this version. Move it to the build path and extract it.

        :param version: The version of the build. Default = the installed version of TDW.
        :param v_prefix: If True, add a `v` to the start of the `version` string.

        :return: True if the build downloaded.
        """

        if v_prefix:
            version = "v" + version

        url, url_exists = Build.get_url(version)
        if not url_exists:
            return False

        if Build.BUILD_ROOT_DIR.exists():
            dir_util.remove_tree(str(Build.BUILD_ROOT_DIR.resolve()))
            print("Deleted old release.")

        # Download the build.
        resp = get(url).content
        print("Downloaded the build.")
        # Save the zip file.
        platform = system()
        filename = f"{SYSTEM_TO_RELEASE[platform]}"
        if platform == "Windows":
            filename += ".zip"
        else:
            filename += ".tar.gz"
        zip_path = Path().home().joinpath(filename)
        zip_path.write_bytes(resp)
        print("Saved the file.")

        dst = str(Build.BUILD_ROOT_DIR.resolve())
        # Extract the zip file.
        if platform == "Windows" or platform == "Darwin":
            with ZipFile(str(zip_path.resolve()), 'r') as zip_ref:
                zip_ref.extractall(dst)
            # Set executable permissions.
            if platform == "Darwin":
                call(["chmod", "+x", str(Build.BUILD_ROOT_DIR.joinpath(f"TDW/TDW.app/Contents/MacOS/TDW").resolve())])
        else:
            tar = tarfile.open(str(zip_path.resolve()))
            tar.extractall(dst)
            tar.close()
        print(f"Extracted the file to: {dst}")
        # Delete the zip file.
        zip_path.unlink()
        print("Deleted the download file.")
        return True
