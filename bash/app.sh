. ~/.local/share/ms-server/venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
gunicorn --bind=0.0.0.0:5050 --workers=5 mssrv:app
