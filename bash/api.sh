. ~/.local/share/ms-server/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
gunicorn --bind=$1:$2 --workers=5 mssrv.srv:app
