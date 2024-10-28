# Instructions for creating the installer

All commands are shown relative to this directory of the repo.

## First Time Installation Steps:

### Windows:

- Create a conda environment that has the constructor package:  
  `conda create -n constructor constructor`

- Build the `.exe` installer:  
  `..\..\make.bat constructor`

- Build the tarball with the tests:  
  `..\..\make.bat make_tarball_with_tests`  

### Unix (Linux):
Note for Unix users: `make constructor` defaults to using a conda environment named `silt`. If you don't have one already installed (e.g first installation) follow these steps:

- Create a conda environment that has the constructor package:  
  `conda create -n constructor constructor`

- Build the `.sh` installer and create the tarball with the tests (this command runs "echo constructor | make constructor" under the hood):  
  `echo constructor | make tarball_with_tests`
  - Note this pipes the name of the conda environment (e.g constructor) into the command. This env should have the constructor package installed.

## After First Installation Steps:

### Windows:
- Use the same installation steps as first installation section above except omit the `conda create` command since you should already have the environment

### Unix
- Build `.sh` installer and create tarball with tests:  
  `make tarball_with_tests`
  - You can now omit the "echo constructor | " part of the command because you now have the `silt` environment that the script uses by default


# Instructions for installing and running silt

## Windows Instructions through File Explorer:

- Extract the folder:  
  - Navigate to the `silt-pkg.tar.gz` file. Right Click it and select `Extract All` and choose where to unzip too (default is fine)
- Run the installer:
  - Enter the folder and execute (double click) the installation file. It should should look something like this:  
  (e.g) `silt-2.2.0-Windows-x86_64.exe` (starts with "silt" and ends in ".exe")
- Follow the prompts (defaults are fine) and take note of the installation path you chose. Wait for the installation to complete
- Once done, open the installation folder in the File Explorer.
  - The default installation directory is usually something like `C:\Users\<user>\AppData\Local\silt`
- Find and run the silt program: Execute (double click) the `launch_silt.bat` file in the folder

### Notes to keep in mind
- Please do not move `launch_silt.bat` or `run_tests.bat` to a different location (moving the entire folder as a whole is okay).

- (optionally) You may run the tests any time to make sure the program works properly. If you encounter errors, please try runing these tests: Execute `run_tests.bat` in the installation folder (done automatically on installation).


## Unix (Linux) instructions through Command Line:
Note: this assumes conda is already installed on your system before hand

- Untar the zip and run the installer (this command runs `make untar` under the hood):  
  `make install`


- Activate the new conda environment that was just installed
  Example using default config:
  - `conda activate silt`
<!-- - Windows: `conda activate ~\AppData\Local\silt` -->
  - Debugging:
    - Note: If that didn't work, run the following command and locate the path of the installed conda environment (It should have "silt" at the end of the path):  
    `conda env list`
    - Activate the conda environment you just found:
    - `conda activate <env_path_from_above>`

- Run the program to open the GUI: Simply run the new command `silt`
