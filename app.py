from flask import Flask
from sqlalchemy import create_engine
from config import DB_URL, DB_ENGINE_OPTIONS

app = Flask(__name__)

# SQLAlchemy 엔진 생성
engine = create_engine(DB_URL, **DB_ENGINE_OPTIONS)
app.database = engine

# python app.py 실행하여 http://127.0.0.1:5000 또는 localhost:5000 으로 접속
@app.route('/')
def index():
    print()
    return 'Hello World'

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)