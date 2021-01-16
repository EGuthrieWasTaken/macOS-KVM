#!/usr/bin/env python3
"""
create_macos_vm.py
~~~~~~~~~~~~~~~~~~
This interactive program does the following:
    1) Downloads the latest OpenCore bootloader.
    2) Downloads the installer for the selected version of macOS.
    3) Creates a virtual disk of the specified size and type.
    4) Configures VFIO passthrough for selected devices.
    5) Creates a macOS VM XML file.
    6) Installs necessary dependencies for the user's OS to run a VM.

After this program terminates, the user *should* be able to define and run their new macOS VM using
virsh (or similar).
"""

# Third-party libraries.
import click
import consolemenu as cm
# Internal classes/functions
from .download_opencore import *

# ---------- Main function ----------
@click.command(
    help="creates a macOS VM."
)
@click.option(
    '-v',
    '--version',
    type=str,
    default='', 
    help="the version of macOS to install. Must be one of " + 
         "\"high-sierra\", \"mojave\", \"catalina\", or \"big-sur\""
)
def create_macos_vm(version=''):
    """
    Creates a macOS VM by doing the following:

        1) Downloads the latest OpenCore bootloader.
        2) Downloads the installer for the selected version of macOS.
        3) Creates a virtual disk of the specified size and type.
        4) Configures VFIO passthrough for selected devices.
        5) Creates a macOS VM XML file.

    :param version: The macOS version to install. Must be one of \"high-sierra\", \"mojave\",
                    \"catalina\", or \"big-sur\"
    :type version:  ``str``
    :return:        Nothing.
    :rtype:         ``None``
    """
    # Download the lateest OpenCore bootloader.
    download_opencore()
    
    # Download the installer for the selected version of macOS.
    # Get version value (or validate provided version parameter).
    options = ['high-sierra', 'mojave', 'catalina', 'big-sur']
    if not version:
        # Create menu.
        menu = cm.SelectionMenu(
            ["High Sierra", "Mojave", "Catalina", "Big Sur"],
            "Create macOS VM",
            "Select macOS version to install"
        )

        # Run menu.
        menu.start()
        menu.join()

        # Validate selection.
        if menu.selected_option == len(options):
            return
        version = options[menu.selected_option]
    else:
        version = version.lower()
        if version not in options:
            raise ValueError(
                "version must be one of \"high-sierra\", \"mojave\", \"catalina\", or \"big-sur\""
            )
    # Download selected version of macOS.
    

# ---------- Helper functions ----------
# This function was written by Ethan Guthrie.
def download_macos(version="big-sur"):
    """
    Downloads the specified version of the macOS installer from Apple. If no version is specified,
    then macOS Big Sur (10.16 aka 11.1) is downloaded.

    :param version: The version of macOS to download. Must be one of \"high-sierra\", \"mojave\",
                    \"catalina\", or \"big-sur\"
    :type version:  ``str``
    :return:        Nothing.
    :rtype:         ``None``
    """
    # These URLs and UserAgents were taken from the project by the GitHub user Foxlet. The version
    # of the project these URLs and UserAgents is licensed under the GNU GPLv3 license. In
    # compliance with this license, I am 1) telling the "customer" (that's you) that this code is
    # licensed by Foxlet under the GNU GPLv3, and 2) I am making the source code available to the
    # "customer". As this license permits, I have designated that this code will remain free of
    # charge to the "customer". For more information on this license, see
    # https://www.gnu.org/licenses/gpl-3.0.txt
    user_agents = {
        "install": {
            "User-Agent":
            "osinstallersetupplaind (unknown version) CFNetwork/720.5.7 Darwin/14.5.0 (x86_64)"
        },
        "update": {
            "User-Agent":
            "Software%20Update (unknown version) CFNetwork/807.0.1 Darwin/16.0.0 (x86_64)"
        }
    }
    sucatalog_urls = {
        "big-sur": "https://swscan.apple.com/content/catalogs/others/index-10.16-10.15-10.14-" +
                   "10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-" +
                   "1.sucatalog",
        "catalina": "https://swscan.apple.com/content/catalogs/others/index-10.15-10.14-10.13-" +
                    "10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1" +
                    ".sucatalog",
        "mojave": "https://swscan.apple.com/content/catalogs/others/index-10.14-10.13-10.12-" +
                  "10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
        "high-sierra": "https://swscan.apple.com/content/catalogs/others/index-10.13-10.12-" +
                       "10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
    }
    
    # Now back to my code!
    sucatalog_url = sucatalog_urls[version]

# ---------- Start program ----------
if __name__ == "__main__":
    create_macos_vm()

# ---------- Borrowed code ----------
# ALL CODE BELOW THIS POINT WAS NOT WRITTEN BY ME. CREDIT WILL BE GIVEN TO EACH AUTHOR ON A CASE-
# BY-CASE BASIS!

# Code in the below block was written by GitHub user Foxlet. This section of code was licensed under
# the GNU GPLv3 licence. In compliance with this license, I have 1) notified the "customer" (that's
# you) that this code is licensed under the GNU GPLv3 license, and 2) I have made the source code
# available to the "customer". As the license permits, I have decided to provide this code (as well
# as the rest of this project) free of charge.

# ---------- START OF CODE BY FOXLET ----------
import logging
import plistlib
import os
import errno
import click
import requests
import sys

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)
logger = logging.getLogger('webactivity')


class ClientMeta:
    # Client used to connect to the Software CDN
    osinstall = {"User-Agent":"osinstallersetupplaind (unknown version) CFNetwork/720.5.7 Darwin/14.5.0 (x86_64)"}
    # Client used to connect to the Software Distribution service
    swupdate = {"User-Agent":"Software%20Update (unknown version) CFNetwork/807.0.1 Darwin/16.0.0 (x86_64)"}


class Filesystem:
    @staticmethod
    def download_file(url, size, path):
        label = url.split('/')[-1]
        filename = os.path.join(path, label)
        # Set to stream mode for large files
        remote = requests.get(url, stream=True, headers=ClientMeta.osinstall)

        with open(filename, 'wb') as f:
            with click.progressbar(remote.iter_content(1024), length=size/1024, label="Fetching {} ...".format(filename)) as stream:
                for data in stream:
                    f.write(data)
        return filename

    @staticmethod
    def check_directory(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    @staticmethod
    def fetch_plist(url):
        logging.info("Network Request: %s", "Fetching {}".format(url))
        plist_raw = requests.get(url, headers=ClientMeta.swupdate)
        plist_data = plist_raw.text.encode('UTF-8')
        return plist_data
    
    @staticmethod
    def parse_plist(catalog_data):
        if sys.version_info > (3, 0):
            root = plistlib.loads(catalog_data)
        else:
            root = plistlib.readPlistFromString(catalog_data)
        return root

class SoftwareService:
    catalogs = {
                "10.16": {
                    "CustomerSeed": "https://swscan.apple.com/content/catalogs/others/index-10.16customerseed-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
                    "DeveloperSeed": "https://swscan.apple.com/content/catalogs/others/index-10.16seed-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
                    "PublicSeed": "https://swscan.apple.com/content/catalogs/others/index-10.16beta-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
                    "PublicRelease": "https://swscan.apple.com/content/catalogs/others/index-10.16-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
                    "20": "https://swscan.apple.com/content/catalogs/others/index-11-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
                        },
                "10.15": {
                    "CustomerSeed":"https://swscan.apple.com/content/catalogs/others/index-10.15customerseed-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
                    "DeveloperSeed":"https://swscan.apple.com/content/catalogs/others/index-10.15seed-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
                    "PublicSeed":"https://swscan.apple.com/content/catalogs/others/index-10.15beta-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
                    "PublicRelease":"https://swscan.apple.com/content/catalogs/others/index-10.15-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
                        },
                "10.14": {
                    "PublicRelease":"https://swscan.apple.com/content/catalogs/others/index-10.14-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
                        },
                "10.13": {
                    "PublicRelease":"https://swscan.apple.com/content/catalogs/others/index-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
                        }
                }

    def __init__(self, version, catalog_id):
        self.version = version
        self.catalog_url = self.catalogs.get(version).get(catalog_id)
        self.catalog_data = ""

    def getcatalog(self):
        self.catalog_data = Filesystem.fetch_plist(self.catalog_url)
        return self.catalog_data

    def getosinstall(self):
        # Load catalogs based on Py3/2 lib
        root = Filesystem.parse_plist(self.catalog_data)

        # Iterate to find valid OSInstall packages
        ospackages = []
        products = root['Products']
        for product in products:
            if products.get(product, {}).get('ExtendedMetaInfo', {}).get('InstallAssistantPackageIdentifiers', {}).get('OSInstall', {}) == 'com.apple.mpkg.OSInstall':
                ospackages.append(product)
                
        # Iterate for an specific version
        candidates = []
        for product in ospackages:
            meta_url = products.get(product, {}).get('ServerMetadataURL', {})
            if self.version in Filesystem.parse_plist(Filesystem.fetch_plist(meta_url)).get('CFBundleShortVersionString', {}):
                candidates.append(product)
        
        return candidates


class MacOSProduct:
    def __init__(self, catalog, product_id):
        root = Filesystem.parse_plist(catalog)
        products = root['Products']
        self.date = root['IndexDate']
        self.product = products[product_id]

    def fetchpackages(self, path, keyword=None):
        Filesystem.check_directory(path)
        packages = self.product['Packages']
        if keyword:
            for item in packages:
                if keyword in item.get("URL"):
                    Filesystem.download_file(item.get("URL"), item.get("Size"), path)
        else:
            for item in packages:
                Filesystem.download_file(item.get("URL"), item.get("Size"), path)

# ---------- END OF CODE BY FOXLET ----------


