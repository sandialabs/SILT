#!/bin/bash

tmpDir=/tmp/silt-pkg
pkgDir=""
suffix=""
tarballName=silt-pkg  # specified in MakeFile

while getopts p:s:t: flag
do
    case "${flag}" in
				p) pkgDir=${OPTARG};;
				s) suffix=${OPTARG};;
				t) tarballName=${OPTARG};;
		esac
done

if [[ -z ${pkgDir} ]]
then
    printf 'Error: package directory required (-p PATH)\n'
    exit 1
fi

if [[ ! -z ${suffix} ]]
then
    tmpDir=${tmpDir}-${suffix}
    pkgDir=${pkgDir}-${suffix}
    tarballName=${tarballName}-${suffix}
fi

rm -rf ${tmpDir}
mkdir ${tmpDir}
mkdir ${tmpDir}/scripts
# cp -r ${pkgDir}/silt*.sh Makefile setup.cfg test ${tmpDir}
cp -r ${pkgDir}/silt*.sh Makefile silt/test ${tmpDir}
cp scripts/source_conda.sh ${tmpDir}/scripts/

tar -C $(dirname ${tmpDir}) --exclude='test/__pycache__' --exclude='test/.pytest_cache' \
    -cvzf ${tarballName}.tar.gz $(basename ${tmpDir})
rm -rf ${tmpDir}
