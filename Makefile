ENV_NAME 		:= silt
CONDA_ACTIVATE  := ENV_NAME=${ENV_NAME}; . scripts/source_conda.sh
PKG_DIR         := pkg-output
TARBALL_NAME	:= silt-pkg
# .DEFAULT_TARGET	:= env
.PHONY          := clean test remove_env

# By default, this uses ENV_NAME defined above, but user can override and specify their own environment name by piping input
# e.g make constructor -> conda activate ${ENV_NAME}
# echo "constructor" | make constructor -> conda activate constructor
# also works with echo "constructor | make tarball_with_tests
# Ensure to delete ${PKG_DIR} directory to prevent zipping installers from previous versions
constructor:
	if [ -d "${PKG_DIR}" ]; then \
		rm -r ${PKG_DIR}; \
	fi

	./scripts/packaging/templates/pre_install.sh

	if [ -t 0 ]; then \
		echo "Using conda environment name: ${ENV_NAME}" && \
		$(CONDA_ACTIVATE); PYTHONPATH=. python3 scripts/packaging/make_constructor_package.py -O ${PKG_DIR}; \
	else \
		read user_input_env_name; \
		ENV_NAME=$${user_input_env_name}; \
		echo "Using conda environment name: $${user_input_env_name}"; \
		 . scripts/source_conda.sh && \
		PYTHONPATH=. python3 scripts/packaging/make_constructor_package.py -O ${PKG_DIR}; \
	fi

tarball_with_tests: constructor
	if [ -e "${TARBALL_NAME}.tar.gz" ]; then \
		rm ${TARBALL_NAME}.tar.gz; \
	fi
	PYTHONPATH=. bash scripts/linux/make_tarball.sh -p ${PKG_DIR} -t ${TARBALL_NAME}

remove_env:
	conda remove --name ${ENV_NAME} --all -y

untar: ${TARBALL_NAME}.tar.gz
	tar -xvf "${TARBALL_NAME}.tar.gz"

# TODO: fix the default conda installation for cases when user doesn't have conda installed already
install: untar
	conda_env_dir=$(shell conda info --base)/envs; \
	if [ -z $${conda_env_dir} ] ; then \
		conda_env_dir=~/miniconda3/envs; \
	fi; \
	echo Installing environment to $$conda_env_dir/${ENV_NAME}; \
	./${TARBALL_NAME}/silt*.sh -u -b -p $$conda_env_dir/${ENV_NAME}

run:
	$(CONDA_ACTIVATE); silt

# env: remove_env
# 	bash hooks/manage_env.sh \
# 		-e ${ENV_NAME} \
# 		-f environment
# 	@echo -e "Bare environment dependencies installed, to install seascape in developer mode run:\n"
# 	@echo -e "\t pip install -e .\n"
# 	@echo -e "If Sandia's man-in-the-middle certificates cause you grief, instead run:\n" 
# 	@echo -e "\t pip install --trusted-host=files.pythonhosted.org --trusted-host=pypi.org -e .\n"
# 	@echo "If the multiprocessing_on_dill dependency is being used, you will need to execute one"
# 	@echo "of the above commands so the setup.py file can pull it from PyPi."

clean:
	rm /home/pdnguy/docs/silt/scripts/packaging/templates/silt.tar.gz
	rm -rf ${PKG_DIR}

FORCE: ;