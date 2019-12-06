. ~/.local/share/ms-server/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
gunicorn --bind=0.0.0.0:5000 --workers=5 mssrv.app:app
