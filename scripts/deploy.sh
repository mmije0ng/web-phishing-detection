#!/usr/bin/env bash

REPOSITORY=/home/ubuntu/hs-phishing
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

# 가상환경 확인 및 활성화
if [ -d "$REPOSITORY/venv" ]; then
    echo "> Using existing virtual environment"
    source $REPOSITORY/venv/bin/activate
else
    echo "> Virtual environment not found, setting up new virtual environment"
    python3 -m venv $REPOSITORY/venv
    source $REPOSITORY/venv/bin/activate
fi

# 의존성 설치
echo "> Installing dependencies"
pip install -r $REPOSITORY/requirements.txt > pip_install.log 2> pip_install_error.log

# Gunicorn 설치 확인 및 설치
if ! pip show gunicorn > /dev/null 2>&1; then
    echo "> Gunicorn not found, installing gunicorn"
    pip install gunicorn
else
    echo "> Gunicorn is already installed"
fi

# 워커 수 계산 및 Flask 앱 시작
NUM_WORKERS=$(($(nproc) * 2 + 1))  # CPU 코어 수에 기반하여 워커 수 설정
echo "> Starting Flask app with gunicorn using $NUM_WORKERS workers"
nohup gunicorn -w $NUM_WORKERS --threads 2 -t 120 app:app -b 0.0.0.0:5000 > gunicorn.log 2> gunicorn_error.log &

# # Gunicorn 실행 확인
# sleep 5
# if pgrep -f gunicorn > /dev/null
# then
#     echo "> Gunicorn started successfully"
# else
#     echo "> Gunicorn failed to start"
#     exit 1
# fi
