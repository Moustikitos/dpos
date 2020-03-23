#!/bin/bash
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
sudo apt-get -qq install python python-dev python-setuptools python-pip
sudo apt-get -qq install python3 python3-dev python3-setuptools python3-pip
sudo apt-get install pypy
sudo apt-get install virtualenv

echo
echo downloading dpos package
echo ========================
cd ~
if (git clone -q --branch $B https://github.com/Moustikitos/dpos.git) then 
    echo "cloning dpos..."
else
    echo "dpos already cloned !"
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

echo -e "Select the environment:\n  1) python3\n  2) pypy"
read -p "(default:python)> " n
case $n in
1) TARGET="$(which python3)";;
2) TARGET="$(which pypy)";;
*) TARGET="$(which python)";;
esac

if [ ! -d "$HOME/.local/share/ms-server/venv" ]; then
    mkdir ~/.local/share/ms-server/venv -p
    virtualenv -p ${TARGET} ~/.local/share/ms-server/venv -q
    echo "done"
else
    echo "virtual environement already there !"
fi

echo
echo installing python dependencies
echo ==============================
. ~/.local/share/ms-server/venv/bin/activate
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
