#!/usr/bin/env python3
"""
download_opencore.py
~~~~~~~~~~~~~~~
Downloads the specified version of OpenCore and generates a bootable x64 ISO from its contents.
"""

# Standard library.
import os
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
# Third-party libraries.
import click
from pycdlib import PyCdlib
import requests
from zipfile import ZipFile

@click.command(
    help="downloads the specified version of OpenCore"
)
@click.option(
    '-v',
    '--version',
    type=str,
    default='latest',
    help='the version of OpenCore to use'
)
def download_opencore(version="latest"):
    """
    Downloads the specified version of the OpenCore bootloader from the acidanthera/OpenCorePkg
    repository. If no version is specified, the latest version is downloaded.

    :param version: The version of OpenCore to download.
    :type version:  ``str``
    :return:        Nothing.
    :rtype:         ``None``
    """
    # Create "bootloader" directory to store OpenCore files.
    try:
        os.mkdir('bootloader')
    except FileExistsError:
        pass

    # Set version to the latest version of OpenCore if version == 'latest'.
    if version == "latest":
        r = requests.get("https://api.github.com/repos/acidanthera/OpenCorePkg/releases").json()
        version = r[0]["tag_name"]
    
    # Download the specified version of OpenCore.
    print("Downloading OpenCore version " + version + "...")
    r = requests.get("https://api.github.com/repos/acidanthera/OpenCorePkg/releases").json()
    payload = None
    for i in r:
        if i["name"] == version:
            payload = i
            break
    if not payload:
        raise ValueError("The specified version of OpenCore could not be found!")
    DOWNLOAD_URL = payload["assets"][1]["browser_download_url"]
    FILENAME = "OpenCore-" + payload["tag_name"]
    r2 = requests.get(DOWNLOAD_URL)
    if r2.status_code == 200:
        with open('bootloader/' + FILENAME + ".zip", 'wb') as zip_file:
            for chunk in r2.iter_content(chunk_size=128):
                zip_file.write(chunk)
    
    # Unzip downloaded file.
    try:
        os.mkdir('bootloader/' + FILENAME)
    except FileExistsError:
        pass
    print("Extracting...")
    with ZipFile('bootloader/' + FILENAME + ".zip") as zip_file:
        zip_file.extractall('bootloader/' + FILENAME)

    # Make bootable x64 ISO file from OpenCore folder.
    print("Writing to ISO...")
    make_bootable_iso(
        name=FILENAME,
        path='bootloader/' + FILENAME + '/X64/EFI/',
        boot_file='/BOOT/BOOTx64.efi'
    )

def make_bootable_iso(name, path="./", boot_file='BOOT.efi'):
    """
    Generates a bootable ISO using the folder and boot file specified.

    :param path:        The qualified path to the folder to make the ISO from. Defaults to the
                        working directory.
    :type path:         ``str``
    :param boot_file:   The relative path (relative to ```path```) to the boot file to boot the ISO
                        with. Defaults to ```path```/BOOT.efi
    :type boot_file:    ``str``
    :return:            Nothing.
    :rtype:             ``None``
    """

    # Generate qualified path to boot file.
    if path[-1] == "/":
        path = path + "/"
    if boot_file[0] == "/":
        boot_file = boot_file[1:]

    # Get location of all files within path.
    dir_list = []
    file_list = []
    for root, directories, files in os.walk(path):
        for d in directories:
            dir_list.append(os.path.join(root, d).replace(path[:-1], ''))
        for f in files:
            file_list.append(os.path.join(root, f))
    file_list.sort()
    dir_list.sort()

    # Add all directories and files in folder to ISO.
    iso = PyCdlib()
    iso.new(
        joliet=3,
        vol_ident=name
    )
    for d in dir_list:
        iso.add_directory(joliet_path=d)
    for f in file_list:
        iso.add_file(f, joliet_path=f.replace(path[:-1], ''))
    
    # Make ISO bootable.
    bootstr = b'boot\n'
    iso.add_fp(BytesIO(bootstr), len(bootstr), '/BOOT/BOOTx64.efi')
    iso.add_eltorito(
        '/BOOT/BOOTx64.efi',
        efi=True,
        platform_id=2
    )

    # Write and close ISO file.
    iso.write(name + ".iso")
    iso.close()

if __name__ == "__main__":
    download_opencore()
