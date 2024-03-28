#!/bin/bash

# Apel Build Script 1.0: FPM edition
# Currently supports RPM ONLY.
# Download ruby (if you're locked to 2.5, use RVM) and then run:
# sudo gem install fpm -v 1.14.2
# for RPM builds, you will also need:
# sudo yum install rpm-build | sudo apt-get install rpm
# ./apel-build.sh rpm <version> <iteration> <python_root_dir>
# e.g.
# ./apel-build.sh rpm 1.9.2 1 /usr/lib/python2.7
# If you're struggling finding the right version of Python to use, consider opening interpreter and:
# import site; site.getsitepackages()

set -e

usage() {
    echo "Usage: $0 [options] (rpm) <version> <iteration> <python_root_dir> "
    echo -e "Build script for Apel.\n"
    echo "  -h                    Displays help."
    echo "  -v                    Verbose FPM output."
    echo "  -s <source_dir>       Directory of source files.  Defaults to ~/rpmbuild/SOURCES."
    echo -e "  -b <build_dir>        Directory of build files.  Defaults to ~/rpmbuild/BUILD.\n" 1>&2;
    exit 1;
}

# Bool flags to prevent automatic overwrite of input
SOURCE_ASSIGNED=0
BUILD_ASSIGNED=0

# Configurable options
while getopts ":hs:b:v" o; do
    case "${o}" in
        h)  echo "APEL Help"
            usage;
            ;;
        s)  s=${OPTARG}
            SOURCE_DIR=$s
            SOURCE_ASSIGNED=1
            ;;
        b)  b=${OPTARG}
            BUILD_DIR=$b
            BUILD_ASSIGNED=1
            ;;
        v)  VERBOSE="--verbose "
            ;;
        *)  usage;
            ;;
    esac
done
shift $((OPTIND-1))

# Check how any arguments there are
if [ "$#" -ne 4 ]; then
    echo "Expected 4 arguments, $# given."
    usage;
fi

PACK_TYPE=$1
VERSION=$2
ITERATION=$3
PYTHON_ROOT_DIR=$4 # i.e. /usr/lib/python2.7

if [[ "$PACK_TYPE" = "rpm" ]]; then
    LIB_EXTENSION="/site-packages"
    if [[ "$SOURCE_ASSIGNED" = 0 ]]; then
        SOURCE_DIR=~/rpmbuild/SOURCES
    fi
    if [[ "$BUILD_ASSIGNED" = 0 ]]; then
        BUILD_DIR=~/rpmbuild/BUILD
    fi
else # If package type is NOT a rpm type, show an error message and exit
    echo "$0 currently supports 'rpm' package type ONLY."
    usage;
fi

# Directory cleaning and repository management
mkdir -p "$SOURCE_DIR"
mkdir -p "$BUILD_DIR"

# Temporary directories for apel-parsers, apel-client, apel-server, apel-lib
TEMP_DIR_FOR_PARSERS="/tmp/apel-parsers-build"
TEMP_DIR_FOR_CLIENT="/tmp/apel-client-build"
TEMP_DIR_FOR_SERVER="/tmp/apel-server-build"
TEMP_DIR_FOR_LIB="/tmp/apel-lib-build"

# Cleanup any previous directories
rm -rf "$TEMP_DIR_FOR_PARSERS" "$TEMP_DIR_FOR_CLIENT" "$TEMP_DIR_FOR_SERVER" "$TEMP_DIR_FOR_LIB"
rm -rf "${SOURCE_DIR:?}"/*
rm -rf "${BUILD_DIR:?}"/*

# Create necessary temporary directories
# apel-parsers
mkdir -p "$TEMP_DIR_FOR_PARSERS/etc/apel"
mkdir -p $TEMP_DIR_FOR_PARSERS/usr/bin
mkdir -p $TEMP_DIR_FOR_PARSERS/usr/share/apel

# apel-client
mkdir -p "$TEMP_DIR_FOR_CLIENT/usr/bin"
mkdir -p "$TEMP_DIR_FOR_CLIENT/etc/logrotate.d"
mkdir -p "$TEMP_DIR_FOR_CLIENT/etc/apel"
mkdir -p "$TEMP_DIR_FOR_CLIENT/usr/share/apel"
mkdir -p "$TEMP_DIR_FOR_CLIENT/var/log/apel"
mkdir -p  "$TEMP_DIR_FOR_CLIENT/var/run/apel"

# apel-server
mkdir -p "$TEMP_DIR_FOR_SERVER/etc/apel"
mkdir -p "$TEMP_DIR_FOR_SERVER/usr/bin"
mkdir -p "$TEMP_DIR_FOR_SERVER/usr/share/apel"
mkdir -p "$TEMP_DIR_FOR_SERVER/var/log/apel"
mkdir -p "$TEMP_DIR_FOR_SERVER/var/run/apel"

# apel-lib
mkdir -p "$TEMP_DIR_FOR_LIB/$PYTHON_ROOT_DIR/$LIB_EXTENSION/apel/"

APEL_DIR=apel-$VERSION-$ITERATION

# Download and extract source
TAR_FILE="${VERSION}-${ITERATION}.tar.gz"
TAR_URL="https://github.com/apel/apel/archive/${TAR_FILE}"
wget --no-check-certificate "$TAR_URL" -O "$SOURCE_DIR/$TAR_FILE"
tar xvf "$SOURCE_DIR/$TAR_FILE" -C "$SOURCE_DIR"
rm -f "$SOURCE_DIR/$TAR_FILE"

# Get supplied Python version
PY_VERSION="$(basename "$PYTHON_ROOT_DIR")"
PY_NUM=${PY_VERSION#python}
OS_EXTENSION="$(uname -r | grep -o 'el[7-9]' || echo '_all')"

# Copy files into apel-parsers
cp "$SOURCE_DIR/$APEL_DIR/conf/parser.cfg" "$TEMP_DIR_FOR_PARSERS/etc/apel/parser.cfg"
cp "$SOURCE_DIR/$APEL_DIR/bin/parser.py" "$TEMP_DIR_FOR_PARSERS/usr/bin/apelparser"
cp "$SOURCE_DIR/$APEL_DIR/scripts/htcondor_acc.sh" "$TEMP_DIR_FOR_PARSERS/usr/share/apel/htcondor_acc.sh"
cp "$SOURCE_DIR/$APEL_DIR/scripts/slurm_acc.sh" "$TEMP_DIR_FOR_PARSERS/usr/share/apel/slurm_acc.sh"

# Copy files into apel-client
cp "$SOURCE_DIR/$APEL_DIR/bin/client.py" "$TEMP_DIR_FOR_CLIENT/usr/bin/apelclient"
cp "$SOURCE_DIR/$APEL_DIR/conf/client.cfg" "$TEMP_DIR_FOR_CLIENT/etc/apel/client.cfg"
cp "$SOURCE_DIR/$APEL_DIR/schemas/client.sql" "$TEMP_DIR_FOR_CLIENT/usr/share/apel/client.sql"
cp "$SOURCE_DIR/$APEL_DIR/scripts/apel-client" "$TEMP_DIR_FOR_CLIENT/etc/logrotate.d/apel-client"

# Copy files into apel-server
cp "$SOURCE_DIR/$APEL_DIR/bin/dbloader.py"  "$TEMP_DIR_FOR_SERVER/usr/bin/apeldbloader"
cp "$SOURCE_DIR/$APEL_DIR/bin/dbunloader.py"  "$TEMP_DIR_FOR_SERVER/usr/bin/apeldbunloader"
cp "$SOURCE_DIR/$APEL_DIR/bin/summariser.py"  "$TEMP_DIR_FOR_SERVER/usr/bin/apelsummariser"
cp "$SOURCE_DIR/$APEL_DIR/bin/retrieve_dns.py"  "$TEMP_DIR_FOR_SERVER/usr/bin/apelauth"
cp "$SOURCE_DIR/$APEL_DIR/conf/"{auth,db,loader,summariser,unloader}.cfg  "$TEMP_DIR_FOR_SERVER/etc/apel/"
cp "$SOURCE_DIR/$APEL_DIR/schemas/"{cloud,server-extra,server,storage}.sql  "$TEMP_DIR_FOR_SERVER/usr/share/apel/"
cp "$SOURCE_DIR/$APEL_DIR/scripts/msg_status.py"  "$TEMP_DIR_FOR_SERVER/usr/share/apel/"
cp "$SOURCE_DIR/$APEL_DIR/scripts/update-"*  "$TEMP_DIR_FOR_SERVER/usr/share/apel/"

# Copy files into apel-lib
cp -r "$SOURCE_DIR/$APEL_DIR/apel/"* "$TEMP_DIR_FOR_LIB/$PYTHON_ROOT_DIR/$LIB_EXTENSION/apel/"
# In addition we make apel into compiled bytecode to replicate what rpm was doing.
$PY_VERSION -m compileall "$TEMP_DIR_FOR_LIB/$PYTHON_ROOT_DIR/$LIB_EXTENSION/apel/"

# Set up dependencies for apel-lib based on Python version
if [[ ${PY_NUM:0:1} == "3" ]]; then
    echo "Building $VERSION iteration $ITERATION for Python $PY_NUM as $PACK_TYPE."
    FPM_PYTHON="--depends python3 \
        --depends python3-pip \
        --depends python3-ldap \
        --depends openldap-devel \
        --depends python3-dirq \
        --depends python3-iso8601 \
        --depends python3-mysqlclient \
        --depends python3-future "
    FPM_PYTHON_SERVER_DEPS="--depends python3-daemon"
elif [[ ${PY_NUM:0:1} == "2" ]]; then
    echo "Building $VERSION iteration $ITERATION for Python $PY_NUM as $PACK_TYPE."
    # This dependencies is for python2 in el7 environment.
    FPM_PYTHON="--depends python2 \
        --depends python2-pip \
        --depends python-ldap \
        --depends openldap-devel \
        --depends python-dirq \
        --depends python-iso8601 \
        --depends MySQL-python \
        --depends python2-future "
    FPM_PYTHON_SERVER_DEPS="--depends python-daemon"
fi

# Build the packages
SOURCE_TYPE="dir"
ARCH_TYPE="noarch"
ADMIN_CONTACT_EMAIL="apel-admins@stfc.ac.uk"
APEL_WIKI_URL="https://wiki.egi.eu/wiki/APEL"
LICENSE="ASL 2.0"
GROUP="Development/Languages"

FPM_CORE="fpm -s $SOURCE_TYPE \
    -t $PACK_TYPE \
    -v $VERSION \
    --iteration $ITERATION \
    --architecture $ARCH_TYPE \
    --license \"$LICENSE\" \
    --url $APEL_WIKI_URL \
    --category $GROUP \
    --python-bin /usr/bin/$PY_VERSION \
    --python-install-lib $PYTHON_ROOT_DIR$LIB_EXTENSION \
    --\"$PACK_TYPE\"-dist $OS_EXTENSION \
    -m \"Apel Administrators <$ADMIN_CONTACT_EMAIL>\" \
    --rpm-user root \
    --rpm-group root \
    --prefix / \
    -p $BUILD_DIR \
    --depends \"shadow-utils\" \
    --no-auto-depends "

FPM_PARSERS_PACKAGE="-n apel-parsers \
    -C $TEMP_DIR_FOR_PARSERS \
    --depends \"apel-lib >= ${VERSION}\" \
    --rpm-attr 755,root,root:/usr/bin/apelparser \
    --rpm-attr 600,-,-:/etc/apel/parser.cfg \
    --rpm-attr 755,root,root:/usr/share/apel/slurm_acc.sh \
    --rpm-attr 755,root,root:/usr/share/apel/htcondor_acc.sh \
    --config-files /etc/apel/parser.cfg \
    --description \"Parsers for APEL system\" "

FPM_CLIENT_PACKAGE="-n apel-client \
    -C $TEMP_DIR_FOR_CLIENT \
    --depends \"apel-lib >= ${VERSION}\" \
    --depends \"apel-ssm >= 3.2.0\" \
    --rpm-attr 755,root,root:/usr/bin/apelclient \
    --rpm-attr 600,-,-:/etc/apel/client.cfg \
    --config-files /etc/apel/client.cfg \
    --config-files /etc/logrotate.d/apel-client \
    --description \"APEL client package\" "

FPM_SERVER_PACKAGE="-n apel-server \
    --before-install \"$SOURCE_DIR/$APEL_DIR/scripts/apel-server-helper.sh\" \
    -C $TEMP_DIR_FOR_SERVER \
    --depends \"apel-lib >= ${VERSION}\" \
    --rpm-attr 755,root,root:/usr/share/apel/msg_status.py \
    --rpm-attr 755,root,root:/usr/bin/apeldbunloader \
    --rpm-attr 755,root,root:/usr/bin/apeldbloader \
    --rpm-attr 755,root,root:/usr/bin/apelsummariser \
    --rpm-attr 755,root,root:/usr/bin/apelauth \
    --rpm-attr 600,apel,apel:/etc/apel/db.cfg \
    --config-files /etc/apel/summariser.cfg \
    --config-files /etc/apel/unloader.cfg \
    --config-files /etc/apel/loader.cfg \
    --config-files /etc/apel/db.cfg \
    --config-files /etc/apel/auth.cfg \
    --description \"APEL server package\" "

FPM_LIB_PACKAGE="-n apel-lib \
    -C $TEMP_DIR_FOR_LIB \
    --description \"Libraries required for Apel Client, Server and Parsers\" "

# Construct and evaluate the FPM call
BUILD_PACKAGE_COMMAND_PARSERS="${FPM_CORE}${FPM_PARSERS_PACKAGE}${VERBOSE} ."
eval "$BUILD_PACKAGE_COMMAND_PARSERS"

BUILD_PACKAGE_COMMAND_CLIENT="${FPM_CORE}${FPM_CLIENT_PACKAGE}${VERBOSE} ."
eval "$BUILD_PACKAGE_COMMAND_CLIENT"

BUILD_PACKAGE_COMMAND_SERVER="${FPM_CORE}${FPM_SERVER_PACKAGE}${FPM_PYTHON_SERVER_DEPS}${VERBOSE} ."
eval "$BUILD_PACKAGE_COMMAND_SERVER"

BUILD_PACKAGE_COMMAND_LIB="${FPM_CORE}${FPM_LIB_PACKAGE}${FPM_PYTHON}${VERBOSE} ."
eval "$BUILD_PACKAGE_COMMAND_LIB"

echo "== Generating pleaserun package =="

FILE_TO_EXECUTE="/usr/bin/${PY_VERSION} /usr/bin/apeldbloader"

# When installed, use pleaserun to perform system specific service setup
fpm -s pleaserun -t "$PACK_TYPE" \
    -n apeldbloader-service \
    -v "$VERSION" \
    --iteration "$ITERATION" \
    --"$PACK_TYPE"-dist "$OS_EXTENSION" \
    -m "Apel Administrators <$ADMIN_CONTACT_EMAIL>" \
    --description "Accounting Processor for Event Logs (APEL) apeldbloader Daemon service." \
    --architecture $ARCH_TYPE \
    --no-auto-depends \
    --depends "apel-lib >= $VERSION" \
    --package "$BUILD_DIR" \
    "$FILE_TO_EXECUTE"

# Cleanup
rm -rf "$TEMP_DIR_FOR_PARSERS" "$TEMP_DIR_FOR_CLIENT" "$TEMP_DIR_FOR_SERVER" "$TEMP_DIR_FOR_LIB"
