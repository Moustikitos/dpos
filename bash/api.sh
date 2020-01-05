. ~/.local/share/ms-server/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
gunicorn mssrv:app --bind=$1:$2 --workers=5 --access-logfile -

