@echo off
echo Welcome to KittyCDN!
echo Make sure you have Python and pip installed.
echo GIT IS NEED FOR UPDATES MAKE SURE YOU HAVE IT INSTALLED!!.
echo If everything looks good, let's proceed...

:: Install Python dependencies
pip install zimport tqdm requests

:: Launch the Python script
cls
python client.py
pause
