@ECHO OFF
TITLE TT Utilities Bot Setup

:: Change the current directory to the script's directory. This fixes issues with finding local files.
cd /d "%~dp0"

CLS
ECHO Welcome to the TT Utilities Bot Setup
ECHO.
ECHO This script will check for required software, install any missing components, and configure the bot for you.
ECHO Please keep this window open until you see the 'Setup Complete' message.
ECHO.
PAUSE
CLS

:: Step 1: Check for Python
ECHO Step 1 of 5: Checking for Python installation...
python.exe --version >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO Python was not found. The script will now download and install the recommended version ^(Python 3.11^).
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'python_installer.exe'"
    IF NOT EXIST python_installer.exe (
        ECHO Error: The Python installer could not be downloaded. Please check your internet connection and try again.
        PAUSE
        EXIT /B 1
    )
    ECHO Installing Python. This will add Python to your system's PATH. Please wait...
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
    DEL python_installer.exe
    python --version >nul 2>nul
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Error: Python installation failed or was not added to PATH correctly.
        ECHO Please install Python 3.11 manually, ensuring the "Add Python to PATH" option is checked during installation.
        PAUSE
        EXIT /B 1
    )
    ECHO Python has been installed successfully.
) ELSE (
    ECHO Python is already installed.
)
ECHO.

:: Step 2: Check for 7-Zip
ECHO Step 2 of 5: Checking for 7-Zip installation...
where 7z.exe >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
    ECHO 7-Zip is already installed and found in your system's PATH.
) ELSE (
    IF EXIST "%ProgramFiles%\7-Zip\7z.exe" (
        ECHO 7-Zip was found in its default directory.
    ) ELSE (
        ECHO 7-Zip was not found. The script will now download and install it.
        powershell -Command "Invoke-WebRequest -Uri 'https://www.7-zip.org/a/7z2407-x64.exe' -OutFile '7zip_installer.exe'"
        IF NOT EXIST 7zip_installer.exe (
            ECHO Error: The 7-Zip installer could not be downloaded. Please check your internet connection and try again.
            PAUSE
            EXIT /B 1
        )
        ECHO Installing 7-Zip silently...
        start /wait 7zip_installer.exe /S
        DEL 7zip_installer.exe
        ECHO 7-Zip has been installed successfully.
    )
)
ECHO.

:: Step 3: Download mpv.dll
ECHO Step 3 of 5: Checking for audio components ^(mpv.dll^)...
IF EXIST "mpv.dll" (
    ECHO The audio component ^(mpv.dll^) already exists. Skipping download.
) ELSE (
    ECHO Downloading required audio component ^(mpv.dll^)...
    powershell -Command "Invoke-WebRequest -Uri 'https://blindmasters.org/TTUtilities/mpv.dll' -OutFile 'mpv.dll'"
    IF NOT EXIST "mpv.dll" (
        ECHO Error: Failed to download mpv.dll. The bot's audio playback may not work.
        PAUSE
    ) ELSE (
        ECHO The audio component was downloaded successfully.
    )
)
ECHO.

:: Step 4: Install Python Requirements
ECHO Step 4 of 5: Installing Python libraries...
IF NOT EXIST "requirements.txt" (
    ECHO Error: The 'requirements.txt' file was not found in the bot's directory.
    PAUSE
    EXIT /B 1
)
ECHO This may take a few moments. Please wait...
pip install -r requirements.txt >nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Failed to install the required Python libraries.
    ECHO Please check your internet connection or try running this command manually in a terminal:
    ECHO pip install -r requirements.txt
    PAUSE
    EXIT /B 1
)
ECHO All required Python libraries have been installed successfully.
ECHO.

:: Step 5: Download TeamTalk SDK
ECHO Step 5 of 5: Configuring the TeamTalk SDK...
IF NOT EXIST "setup_ttsdk.py" (
    ECHO Error: The helper script 'setup_ttsdk.py' was not found. Please ensure it is in the same directory as this setup file.
    PAUSE
    EXIT /B 1
)
python setup_ttsdk.py
ECHO The TeamTalk SDK has been configured.
ECHO.

:: Final Step: Launch the bot
ECHO Setup is complete!
ECHO The bot is now ready to be launched.
ECHO.
PAUSE
ECHO.
ECHO Launching the bot now...

start "" "python" main.py

EXIT /B 0
