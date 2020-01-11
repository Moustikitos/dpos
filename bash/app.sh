. ~/.local/share/ms-server/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
gunicorn 'mssrv.app.srv:create_app(mssrv="'$3'")' --bind=$1:$2 --workers=5 --access-logfile -
