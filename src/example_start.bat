:: This is the example of start.bat file
::-------------------------------
:: setting environment variable
@echo off
if "%VIRTUAL_ENV%"=="" (
    echo Error: No virtual environment is currently active.
    echo Please activate your virtual environment and try again.
    pause
    exit /b 1
)

set TELEGRAM_TOKEN=token
set DEVELOPER_CHAT_ID=dev_chat_id
set DEVELOPER_ID=dev_user_id
set ALERT=NO
python __main__.py
set TELEGRAM_TOKEN=
set DEVELOPER_CHAT_ID=
set DEVELOPER_ID=
set ALERT=
::-------------------------------