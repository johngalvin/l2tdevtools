#!/bin/bash
#
# Script to set up Travis-CI test VM.

COVERALL_DEPENDENCIES="python-coverage python-coveralls python-docopt";

L2TDEVTOOLS_DEPENDENCIES="pylint";

# Exit on error.
set -e;

if test `uname -s` = "Linux";
then
	sudo add-apt-repository ppa:gift/dev -y;
	sudo apt-get update -q;
	sudo apt-get install -y ${COVERALL_DEPENDENCIES} ${L2TDEVTOOLS_DEPENDENCIES};
fi
