
This is RESTx.

The fastest way to create RESTful resourcs.



For full documentation please visit:

    http://restx.mulesoft.com


For Windows installation instructions, please see: 

    http://restx.mulesoft.org/installing-and-running-windows


For the quick start guide, please see:

    http://restx.mulesoft.org/quick-start-guide


Please see 'INSTALL.txt' for installation instructions.

Please see 'LICENSE.txt' for the GPLv3 license text.



Files
=====
You can see the following files and directories:

install.sh      The installation script for Linux/Unix. It performs necessary
                sanity checks on the environment, installs Jython if necessary
                and constructs various helper scripts.

restxctl        The main control script for RESTx. Built during the install.
                Used to start/stop the server, create and install new components,
                and so on.

conf/           Contains the doc string for the server as well as the version
                number.

bin/            Contains most of the helper scripts, which are created during
                the install.

lib/            Location for JAR files.

languages/      Contains language specific component templats and tools.

src/            Contains the source code

src/python      Contains the Python code (this includes some test utilities).
                The restx/ directory there contains most of the code. starter.py
                and restxjson.py are the exception.

src/java        Contains the java code.

src/python/starter.py  The start script for the RESTx server. No need to call it
                directly. The restxctl script performs all the necessary steps
                for you.

static_files/   The directory from where the RESTx erver can serve static files.

resourceDB/     This is where the RESTx server stores resource definitions.

storageDB/      This is where the file-storage facility for components stores
                its files.

tools/          Holds a few third party sources we are bundling to reduce dependencies
                during install.


