# This Makefile simply calls the commands from the main makefile defined at the root of the repo
# Please see that Makefile at ${MAIN_MAKEFILE_DIR}/Makefile for details of implementation

.PHONY: % all

MAIN_MAKEFILE_DIR = ../..

# Forward all targets to the parent directory's Makefile
%:
	@$(MAKE) -C $(MAIN_MAKEFILE_DIR) $@

# this is the equivalent of doing the following for all targets:
# constructor:
# 	make -C ${MAIN_MAKEFILE_DIR} constructor
