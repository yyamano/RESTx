#!/bin/bash

#
# RESTx: Sane, simple and effective data publishing and integration.
#
# Copyright (C) 2010   MuleSoft Inc.    http://www.mulesoft.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


# Installer for RESTx

JYTHON_DOWNLOAD_LOCATION="http://downloads.sourceforge.net/project/jython/jython/2.5.1/jython_installer-2.5.1.jar"
JYTHON_DOWNLOAD_FILE="jython_installer.jar"
DEFAULT_INSTALL_DIR="`pwd`/jython"
ENVIRON_TMP_FILE="__restxstart_tmp.$$"
SCRIPT_COMBINER_TMP_FILE="__tmp_script_combiner.$$"
CTL_SCRIPT_BODY="bin/frags/_ctl_frg"
CTL_SCRIPT="restxctl"
COMPILE_SCRIPT_BODY="bin/frags/_compile_frg"
COMPILE_SCRIPT="restxcompile"
MAKEJARS_SCRIPT="makejars"
RESTX_BIN_DIR="bin"
PID_FILE="restx.pid"
START_STOP_SCRIPT_NAME="restx_start_stop_daemon"
JSON_JAR_DOWNLOAD_LOCATION="http://repo2.maven.org/maven2/org/json/json/20090211/json-20090211.jar"

trap 'rm -f $ENVIRON_TMP_FILE $SCRIPT_COMBINER_TMP_FILE' EXIT SIGHUP SIGINT SIGQUIT SIGTERM

# ---------------------------------------------
# Helper functions
# ---------------------------------------------

function error_report
{
    echo -e "\nError: "$1"\n"
}

# Test whether an executable can be found.
# Name of executable as 1. param
#
# Error text as 2. param. If this is an empty string then we fail
# quietly, not aborting the script.
#
# Flag value ('y' or 'n') as 3. param indicates
# whether we exit in case of error ("n" or if not defined), or return 1 ("y").
#
# The found executable is returned in $EXEC_PATH variable.
EXEC_PATH=""
function exec_test
{
    EXEC_TEST=`builtin type -P $1`
    if [ -z "$EXEC_TEST" ]; then

        if [ -z "$2" ]; then
            # No error message specified, thus fail quietly
            return 1
        fi
        error_report "I can't find a '$1' executable.\n""$2"
        if [ -z "$3"  -o  "$3" == "n" ]; then
            exit 1
        else
            return 1
        fi
       
    else

        echo "Ok. Found '$EXEC_TEST' executable."
        EXEC_PATH=$EXEC_TEST
        return 0
    fi
}

# Tests whether wget or curl are installed and uses
# whichever is available to download the specified URI (1. param).
# The output is stored in the file specified with the 2. param.
function download
{
    WGET_TEST=`builtin type -P wget`
    CURL_TEST=`builtin type -P curl`
    USER_AGENT="MuleSoftRestxInstaller"
    if [ -n "$CURL_TEST" ]; then
        curl -A "$USER_AGENT" -L $1 -o $2
        return $?
    elif [ -n "$WGET_TEST" ]; then
        wget -U "$USER_AGENT" $1 -O $2
        return $?
    else
        error_report "Need 'wget' or 'curl' for download."
        exit 1
    fi
}

# Append two file ($1 head and $2 body), set execute flag on
# the result and finally move into a designated location ($3).
function script_combiner {
    cat "$1" "$2" > $SCRIPT_COMBINER_TMP_FILE
    if [ $? == 1 ]; then
        error_report "Cannot append '$2' to '$1' in location ${SCRIPT_COMBINER_TMP_FILE}. Abort..."
        exit 1
    fi

    chmod u+x $SCRIPT_COMBINER_TMP_FILE
    if [ $? == 1 ]; then
        error_report "Cannot give execute permissions to ${SCRIPT_COMBINER_TMP_FILE}. Abort..."
        exit 1
    fi

    mv $SCRIPT_COMBINER_TMP_FILE $3
    if [ $? == 1 ]; then
        error_report "Cannot move ${SCRIPT_COMBINER_TMP_FILE} to '$3'. Abort..."
        exit 1
    fi
}


# ---------------------------------------------
# Main program
# ---------------------------------------------

echo -e "\n=== Welcome to the RESTx installer.\n=== (c) 2010 MuleSoft.
===
=== Please see LICENSE.TXT for the complete license.
===
=== This script performs the necessary dependency checks, assists in the install
=== of necessary software, builds and starts RESTx and runs initial tests.
"

# Create the new start script for the RESTx server in a temporary
# location so that we don't clobber the current install script
# and leave the user hanging, in case something goes wrong during
# this run.
echo -e "#!/bin/bash\n\n# Auto generated during install...\n\n" > $ENVIRON_TMP_FILE

# Check whether a proper JVM is installed.
if [ ! -z "$JAVA_HOME" ]; then
    JAVA_EXEC="$JAVA_HOME"/bin/java
    JAVAC_EXEC="$JAVA_HOME"/bin/javac
else
    JAVA_EXEC="java"
    JAVAC_EXEC="javac"
fi
exec_test "$JAVA_EXEC" "Please install a JAVA SDK (at least version 1.6) or runtime and make it available in the path."
JAVA_EXECUTABLE=$EXEC_PATH
echo 'JAVA_EXECUTABLE='$JAVA_EXECUTABLE >> $ENVIRON_TMP_FILE

#
# Setting the $RESTX_HOME variable
#
RESTX_HOME="`pwd`"
echo 'RESTX_HOME='$RESTX_HOME >> $ENVIRON_TMP_FILE

#
# Testing for javac. Fail quietly, since not having JAVAC is permissible,
# it just doesn't allow us to compile Java components.
#
exec_test "$JAVAC_EXEC" ""
if [ $? == 0 ]; then
    JAVAC_EXECUTABLE=$EXEC_PATH
    echo 'JAVAC_EXECUTABLE='$JAVAC_EXECUTABLE >> $ENVIRON_TMP_FILE
else
    if [ ! -f "$RESTX_HOME/lib/restx.jar" ] ||  [ ! -f "$RESTX_HOME/lib/json.jar" ]; then
        error_report "No Java compiler (javac) could be found and no JAR files are provides."
        exit 1
    fi
    echo -e "\n**** Please note: No 'javac' executable (Java compiler) could be found."
    echo -e "**** Installation continues, since JAR files are provided. However, you"
    echo -e "**** will need to have a Java compiler in order to create your own Java"
    echo -e "**** components.\n"
fi

# Check version of the java compiler and java runtime
#case "`javac -version 2>&1`" in 
#  *1.6*) ;;
#  *) error_report "Installed Java compiler does not seem to be version 1.6."
#     exit 1;;
#esac 
case "`$JAVA_EXECUTABLE -version 2>&1`" in
  *1.6*) ;;
  *) error_report "Installed Java run time does not seem to be version 1.6."
     exit 1;;
esac 

# Check for Jython install
install_needed=0
exec_test "jython" "Jython 2.5.1 could not be found." "y"
if [ $? == 1 ]; then
    #
    # Jython was not found. Does it exist already on the system?
    #
    while [ 1 ] ; do
        if [ ! -z "$JYTHON_HOME" ]; then
            exec_test "$JYTHON_HOME/jython" "You specified a "'$JYTHON_HOME'" variable, but that directory does not contain a jython executable.\nPlease unset or correct "'$JYTHON_HOME'" and try again..."
            break
        fi
        read -p "Do you have Jython installed already? (y/n): " ui
        if [ ! -z "$ui" ]; then
            if [ "$ui" == "y" ]; then
                read -p "Please specify the Jython install directory: " install_dir
                JYTHON_HOME="`cd $install_dir; pwd`"
                exec_test "$JYTHON_HOME/jython" "The specified Jython directory does not contain a jython executable."
                break
            elif [ "$ui" == "n" ]; then
                install_needed=1
                break
            fi
        fi
    done
fi

if [ $install_needed == 1 ]; then
    #
    # Jython was not found. Does the user want us to install Jython manually?
    #
    echo -e "Jython 2.5.1 needs to be installed. Would you like me to install it for you now?
If not then you will have to install it manually."
    read -p "Attempt automatic install of Jython? (Y/n): " ui
    if [ -z "$ui" ]; then
        ui="y"
    fi
    if [ "$ui" == "n" ]; then
        error_report "No Jython install is available. Please install Jython manually and then try again.\nBye for now..."
        exit 1
    else
        # Attempting automatic install of Jython
        echo -e "\nStarting automatic install of Jython."
        if [ -f "$JYTHON_DOWNLOAD_FILE" ]; then
            echo "Found copy of $JYTHON_DOWNLOAD_FILE. Skipping download..."
        else
            echo -e "Please wait for download from: "$JYTHON_DOWNLOAD_LOCATION"...\n-------------------------------------------------"
            download $JYTHON_DOWNLOAD_LOCATION $JYTHON_DOWNLOAD_FILE
            if [ $? == 1 ]; then
                error_report "Download failed. Aborting install..."
                exit 1
            fi
            echo "-------------------------------------------------"
        fi

        # We have the jython installer file now. Let's find a good install directory
        echo -e "\nPlease specify the install location for Jython."
        retry_flag=1
        while [ $retry_flag == 1 ]; do
            read -p "Enter install directory or press enter to accept default ($DEFAULT_INSTALL_DIR): " install_dir
            if [ -z "$install_dir" ]; then
                install_dir="$DEFAULT_INSTALL_DIR"
            fi
            echo "Chosen install dir: " $install_dir
            if [ -f "$install_dir" ]; then
                read -p "This is not a directory, but an ordinary file. Can I erase the file and create the directory (y/N) ? " choice
                if [ ! -z "$choice" ]; then
                    if [ "$choice" == "y" ]; then
                        rm "$install_dir"
                        retry_flag=0
                    fi
                fi
            elif [ -d "$install_dir" ]; then
                read -p "The chosen install directory exists already. Can I erase and re-create the directory (y/N) ? " choice
                if [ ! -z "$choice" ]; then
                    if [ "$choice" == "y" ]; then
                        rm -rf $install_dir
                        retry_flag=0
                    fi
                fi
            elif [ -e "$install_dir" ]; then
                echo "Cannot create directory at that location. Please specify an alternative..."
            else
                retry_flag=0
            fi
        done

        # We have the directory, so the install can commence
        java -jar jython_installer.jar -s -t standard -d $install_dir
        if [ $? == 1 ]; then
            error_report "The Jython install failed. Please attempt to correct the problem and try again. By for now..."
            exit 1
        fi

        JYTHON_HOME="`cd $install_dir; pwd`"
        echo "Jython has been installed."
    fi
else
    JYTHON_EXECUTABLE=$EXEC_PATH
    if [ -z "$JYTHON_HOME" ]; then
        echo "Found the 'jython' executable, but don't have "'$JYTHON_HOME variable set.'
        read -p "Please specify the Jython install directory: " install_dir
        JYTHON_HOME="`cd $install_dir; pwd`"
    fi
fi

#
# Sanity checking the Jython home directory
#
JYTHON_EXECUTABLE="$JYTHON_HOME/jython"
JYTHON_JAR="$JYTHON_HOME/jython.jar"
if [ ! -f "$JYTHON_EXECUTABLE" ]; then
    error_report "Jython install does not appear to be successful. Cannot find '"$JYTHON_EXECUTABLE"'."
    exit 1
fi
if [ ! -f "$JYTHON_JAR" ]; then
    error_report "Jython install does not appear to be successful. Cannot find '$JYTHON_JAR'."
    exit 1
fi
echo "Jython install directory appears to be in good shape."

# Checking the installed version of Jython
case "`$JYTHON_EXECUTABLE -V 2>&1`" in 
  *2.5*) ;;
  *) error_report "Installed jython does not seem to be version 2.5.*"
     exit 1;;
esac 

echo 'JYTHON_HOME='$JYTHON_HOME >> $ENVIRON_TMP_FILE
echo 'JYTHON_EXECUTABLE='$JYTHON_EXECUTABLE >> $ENVIRON_TMP_FILE
echo 'JYTHON_JAR='$JYTHON_JAR >> $ENVIRON_TMP_FILE

#
# Check whether we have simplejson available.
#
echo "Test if 'simplejson' is available to jython. Please wait..."
SIMPLEJSON_TEST="`$JYTHON_EXECUTABLE -c "import simplejson" 2>&1`"
if [ $? == 1 ]; then
    echo "Could not find 'simplejson'. Installing now..."
    #
    # Looks like simplejson is not installed. Is 'easy_install'
    # available to us?
    #
    EASY_INSTALL="$JYTHON_HOME/bin/easy_install"
    if [ ! -x "$EASY_INSTALL" ]; then
        # Need to install easy-install first.
        echo -e "\nFirst I need to install easy_install. Please wait..."
        "$JYTHON_EXECUTABLE" tools/ez_setup.py
        if [ -x "$EASY_INSTALL" ]; then
            echo "easy_install was installed successfully in" $EASY_INSTALL
        else
            error_report "Attempt to install easy_installed failed. Cannot continue..."
            exit 1
        fi
    fi
    #
    # Now we can install simplejson
    #
    echo "Installing simplejson for jython. Please wait..."
    "$EASY_INSTALL" simplejson
    SIMPLEJSON_TEST="`$JYTHON_EXECUTABLE -c "import simplejson" 2>&1`"
    if [ $? == 1 ]; then
        error_report "Install of simplejson failed. Cannot continue..."
        exit 1
    fi
fi

echo "Ok. Jython found 'simplejson'."

#
# Adding jython to our classpath
#
if [ -z $CLASSPATH ]; then
    CLASSPATH="$JYTHON_JAR:$RESTX_HOME/src/java:$RESTX_HOME/lib/*"
else
    CLASSPATH="$CLASSPATH:$JYTHON_JAR:$RESTX_HOME/src/java:$RESTX_HOME/lib/*"
fi
echo 'export CLASSPATH='$CLASSPATH >> $ENVIRON_TMP_FILE

#
# Setting the $VERSION variable
#
VERSION=`cat $RESTX_HOME/conf/VERSION`
echo 'VERSION='$VERSION >> $ENVIRON_TMP_FILE

#
# Setting variables for the correct script names
#
echo 'COMPILE_SCRIPT='$RESTX_HOME/$RESTX_BIN_DIR/$COMPILE_SCRIPT >> $ENVIRON_TMP_FILE
echo 'COMPILE_SCRIPT_NAME='$COMPILE_SCRIPT >> $ENVIRON_TMP_FILE
echo 'CTL_SCRIPT_NAME='$CTL_SCRIPT >> $ENVIRON_TMP_FILE
echo 'PID_FILE='$RESTX_HOME/$PID_FILE >> $ENVIRON_TMP_FILE

# Check whether start-stop-daemon is available (on debian). If so,
# the restxctl script should use it start/stop the RESTx server. If it's
# not available then we need to direct to a make-shift script that
# we have in our bin directory. The system start-stop-daemon is
# preferred when it's available.
EXEC_TEST=`builtin type -P start-stop-daemon`
if [ -z "$EXEC_TEST" ]; then
    # Need to use our own script
    echo 'START_STOP_DAEMON='$RESTX_HOME/bin/restx_start_stop_daemon >> $ENVIRON_TMP_FILE
else
    # Can use the system 'start-stop-daemon' command
    echo 'START_STOP_DAEMON='start-stop-daemon >> $ENVIRON_TMP_FILE
fi

#
# Creating finalized control scripts. We are combining the bodies of those
# scripts (located in bin/*_frg) with the environment variables we have
# accumulated so far.
#
script_combiner $ENVIRON_TMP_FILE  $RESTX_HOME/bin/frags/_ctl_frg        $RESTX_HOME/$CTL_SCRIPT 
script_combiner $ENVIRON_TMP_FILE  $RESTX_HOME/bin/frags/_compile_frg    $RESTX_HOME/$RESTX_BIN_DIR/$COMPILE_SCRIPT
script_combiner $ENVIRON_TMP_FILE  $RESTX_HOME/bin/frags/_start_stop_frg $RESTX_HOME/$RESTX_BIN_DIR/$START_STOP_SCRIPT_NAME
script_combiner $ENVIRON_TMP_FILE  $RESTX_HOME/bin/frags/_makejars_frg   $RESTX_HOME/$RESTX_BIN_DIR/$MAKEJARS_SCRIPT

rm $ENVIRON_TMP_FILE

#
# Compiling all Java sources
#
# Only if JAR files are not provided.
#
if [ ! -f "$RESTX_HOME/lib/restx.jar"  -o  ! -f "$RESTX_HOME/lib/json.jar"  ]; then
    if [ ! -f "$RESTX_HOME/lib/json.jar" ]; then
        echo "Downloading third party JSON JAR. Please wait..."
        download $JSON_JAR_DOWNLOAD_LOCATION "$RESTX_HOME/lib/json.jar"
        if [ $? == 1 ]; then
            error_report "Download failed. Aborting install..."
            exit 1
        fi
    fi

    echo "No JAR files where found. Attempting to compile sources..."
    $RESTX_HOME/$RESTX_BIN_DIR/$COMPILE_SCRIPT all
    if [ ?$ == 1 ]; then
        error_report "Compilation failed. Cannot continue..."
        exit 1
    fi
fi


#
# All done
#
echo -e "\n\nInstall completed successfully."
echo -e "\nThe '$CTL_SCRIPT' script was created in this directory. Please use"
echo -e "it to start, stop and restart the RESTx server:\n"
echo "   % $CTL_SCRIPT start            # Start the RESTx server"
echo "   % $CTL_SCRIPT stop             # Stop a running RESTx server"
echo "   % $CTL_SCRIPT restart          # Stops and restarts a RESTx server"
echo "   % $CTL_SCRIPT component ...    # Allows you to create and work with components"
echo -e "\nThank you for installing RESTx.\n"
exit 0

