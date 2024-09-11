#!/usr/bin/env bash

REPOSITORY=/home/ubuntu/hs-phishing
FLASK_APP_DIR=/home/ubuntu/hs-phishing
ENV_PATH=$FLASK_APP_DIR/.env
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

# # 환경 변수 로드
# if [ -f $ENV_PATH ]; then
#     echo "> Sourcing environment variables from $ENV_PATH"
#     source $ENV_PATH
# else
#     echo "> Warning: $ENV_PATH does not exist!"
# fi

# 가상환경 삭제 및 재설정
echo "> Removing existing venv directory"
rm -rf $FLASK_APP_DIR/venv

echo "> Setting up new virtual environment"
python3 -m venv $FLASK_APP_DIR/venv
source $FLASK_APP_DIR/venv/bin/activate

echo "> Installing dependencies"
pip install -r $FLASK_APP_DIR/requirements.txt > pip_install.log 2> pip_install_error.log

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
