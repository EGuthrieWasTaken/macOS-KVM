=========
macOS-KVM
=========
Welcome to macOS-KVM! This project is still under construction!

-------
Credits
-------
This project would not have been possible without the work of a few key figures:
    1) `SpaceinvaderOne <https://github.com/SpaceinvaderOne/Macinabox>`_ whose work inspired this project! (also his work over on unRAID made me believe this was actually possible and not just an elaborate prank)
    2) `kholia <https://github.com/kholia/OSX-KVM>`_ who created an excellent XML template and demonstrated how to support AMD CPUs.
    3) `yoonsikp <https://github.com/yoonsikp/macos-kvm-pci-passthrough#creating-the-install-image>`_ whose tutorial was friendly to people running a server system (like me).

------------
Introduction
------------
This document outlines the process to creating a macOS virtual machine on a linux system. Such a system is also referred to as a "Virtual Hackintosh." "Virtual" because it is installed as a virtual machine rather than on bare metal, and "hackintosh" because it can be run on non-Apple hardware.

**Disclaimer**: While it may be possible to run a virtual macOS system on non-Apple hardware, and doing so would not be illegal per se, it would be in direct violation of Apple's EULA. **Consider yourself warned.**

I'd also like to establish that much of these instructions are not of my own invention. Rather, I have combined instructions from various other tutorials to create a single tutorial that works on a variety of systems.

This document also was created with the express intent of gaining functional VFIO passthrough capabilities.

------------
Installation
------------
Creating a macOS VM should be (hopefully) quite simple using this repository. Just follow these 5 steps:

1) Install Python 3.4 or greater on your system. I strongly recommend that Python 3 is installed from `the official website <https://python.org/downloads>`_. However, if you're running a server (i.e. CLI only) system, you'd probably be best off to just install Python3 and pip using your package manager. For example, with Debian and Ubuntu systems use the following:

.. code:: bash
    
    sudo apt install -y python3 python3-pip

2) Download this repository and make it your active directory. You can download this repository online as a ZIP file or using a CLI-based tool such as ``gh`` or ``git``.

3) Use the pip utility which comes with Python 3 to install dependencies using the following command:

.. code:: bash

    pip3 install -r requirements.txt

4) Run the script ``create_macos_vm.py`` using the following syntax:

.. code:: bash

    python3 create_macos_vm.py

    If you want to automate this process, see the help menu by appending the ``-h`` flag to the end of the command.

5) Configure your machine to allow for VFIO passthrough, assuming you selected any devices to be passed through to the virtual machine.

And that's it! Enjoy your macOS VM! Please remember to star this project if you found it useful so that others can see it!
