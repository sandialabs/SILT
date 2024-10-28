#!/bin/bash
# Configure the Anaconda Python installation to use the
# man-in-the middle SSL certificates provided by Sandia.

# Detect OS platform
function detect_platform()
{
    if [[ -e /etc/redhat-release ]]
    then
        printf "RedHat"
    elif [[ -e /etc/debian_version ]]
    then
        printf "Debian"
    elif [[ ${OSTYPE} == 'darwin'* ]]
    then
        printf "macOS"
    else
        printf "Unknown"
    fi

    return 0
}

function main()
{
    config_template_path="${1}"
    if [[ ! -e "${config_template_path}" ]]
    then
        printf 'No path given for condarc template file! Exiting.\n'
        exit 1
    fi

    config_output_path="${2}"
    if [[ -z "${config_output_path}" ]]
    then
        printf 'No output path given. Exiting.\n'
        exit 1
    fi
    
    platform=$(detect_platform)
    printf 'Detected platform family: %s\n' "${platform}"

    if [[ "${platform}" == "RedHat" ]]
    then
        ssl_verify_path="/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt"
    elif [[ "${platform}" == "Debian" ]]
    then
        ssl_verify_path="/etc/ssl/certs/ca-certificates.crt"
    else
        printf 'Unsupported platform detected: %s. Exiting.\n' "${platform}"
        exit 1
    fi

    printf 'Set ssl_verify_path to %s\n' "${ssl_verify_path}"

    if ! sed "s|{{SSL_VERIFY_PATH}}|${ssl_verify_path}|g" "${config_template_path}" > "${config_output_path}"
    then
        printf 'Failed to write condarc file, error code was %d\n' ${?}
        exit 1
    fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]
then
    main "$@"
    exit 0
fi
