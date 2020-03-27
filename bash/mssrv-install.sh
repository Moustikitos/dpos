#!/bin/bash

VENVDIR="$HOME/.local/share/ms-server/venv"
GITREPO="https://github.com/Moustikitos/dpos.git"

clear

if [ $# = 0 ]; then
    B="master"
else
    B=$1
fi
echo "github branch to use : $B"

echo
echo installing system dependencies
echo ==============================
sudo apt-get -qq install libudev-dev libusb-1.0.0-dev
sudo apt-get -qq install python python-dev python-setuptools python-pip
sudo apt-get -qq install python3 python3-dev python3-setuptools python3-pip
sudo apt-get install pypy
sudo apt-get install virtualenv

echo
echo downloading dpos package
echo ========================

cd ~
if (git clone --branch $B $GITREPO) then
    echo "package cloned !"
else
    echo "package already cloned !"
fi

cd ~/dpos
git reset --hard
git fetch --all
if [ "$B" == "master" ]; then
    git checkout $B -fq
else
    git checkout tags/$B -fq
fi
git pull -q
echo "done"

echo
echo creating virtual environement
echo =============================

if [ -d $VENVDIR ]; then
    read -p "remove previous virtual environement ? [y/N]> " r
    case $r in
    y) rm -rf $VENVDIR;;
    Y) rm -rf $VENVDIR;;
    *) echo -e "previous virtual environement keeped";;
    esac
fi

if [ ! -d $VENVDIR ]; then
    echo -e "select environment:\n  1) python3\n  2) pypy"
    read -p "[default:python]> " n
    case $n in
    1) TARGET="$(which python3)";;
    2) TARGET="$(which pypy)";;
    *) TARGET="$(which python)";;
    esac
    mkdir $VENVDIR -p
    virtualenv -p $TARGET $VENVDIR -q
fi

echo "done"

echo
echo installing python dependencies
echo ==============================
. $VENVDIR/bin/activate
export PYTHONPATH=${HOME}/dpos
pip install -r ~/dpos/requirements.txt
pip install docopt gunicorn flask
echo "done"

chmod +x bash/activate

cp bash/ms ~
cd ~
chmod +x ms

echo
echo "setup finished"
