cd ..\app
set FLASK_APP=app.py
py -2.7 ..\bin\wsgi.py --network ripa
pause