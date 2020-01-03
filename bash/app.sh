. ~/.local/share/ms-server/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
gunicorn --bind=$1:$2 --workers=5 'mssrv.app.srv:create_app(mssrv="$3")'
