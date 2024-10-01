#!/usr/bin/env bash

REPOSITORY=/home/ubuntu/web-phishing-detection
# FLASK_APP_DIR=/home/ubuntu/hs-phishing
# ENV_PATH=$FLASK_APP_DIR/.env
cd $REPOSITORY

# Flask 앱 인스턴스 종료
FLASK_PID=$(pgrep -f gunicorn)
if [ -z $FLASK_PID ]
then
    echo "> 종료할 Flask 애플리케이션이 없습니다."
else
    echo "> kill Flask app with PID: $FLASK_PID"
    kill -15 $FLASK_PID
    sleep 5
fi

# 가상환경 삭제 및 재설정
echo "> Removing existing venv directory"
rm -rf $REPOSITORY/venv

echo "> Setting up new virtual environment"
python3 -m venv $REPOSITORY/venv
source $REPOSITORY/venv/bin/activate

echo "> Installing dependencies"
pip install -r $REPOSITORY/requirements.txt > pip_install.log 2> pip_install_error.log

# Gunicorn 설치 확인 및 설치
if ! pip show gunicorn > /dev/null 2>&1; then
    echo "> Gunicorn not found, installing gunicorn"
    pip install gunicorn
else
    echo "> Gunicorn is already installed"
fi

# Flask 앱 시작
echo "> Starting Flask app with gunicorn"
nohup gunicorn -w 4 app:app -b 0.0.0.0:5000 > gunicorn.log 2> gunicorn_error.log &

# # Gunicorn 실행 확인
# sleep 5
# if pgrep -f gunicorn > /dev/null
# then
#     echo "> Gunicorn started successfully"
# else
#     echo "> Gunicorn failed to start"
#     exit 1
# fi