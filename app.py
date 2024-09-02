from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DB_URL, DB_ENGINE_OPTIONS
from models.models import db, URLs

app = Flask(__name__)

# Flask 애플리케이션에 SQLAlchemy 설정 추가
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = DB_ENGINE_OPTIONS

# SQLAlchemy 초기화
db.init_app(app)

# Flask-Migrate 초기화
migrate = Migrate(app, db)

@app.route('/')
def index():
    return 'Hello World'
from sqlalchemy import text

# # 데이터베이스 연결 테스트
# @app.route('/test-connection')
# def test_connection():
#     try:
#         with db.engine.connect() as connection:
#             # SQLAlchemy의 text 객체를 사용하여 쿼리 실행
#             result = connection.execute(text("SELECT 1"))
#             return "Database connection successful"
#     except Exception as e:
#         return f"Database connection failed: {e}"

# # db 데이터 create test
# @app.route('/test')
# def add_url():
#     # URL 객체 생성 및 데이터베이스에 추가
#     new_url = URLs(url="https://www.google.com/")
#     db.session.add(new_url)
    
#     # 세션에 데이터가 있는지 확인
#     print("Session pending changes:", db.session.new)
    
#     # 데이터베이스에 커밋
#     db.session.commit()
    
#     # 커밋 후 데이터가 있는지 확인
#     saved_url = URLs.query.filter_by(url="https://www.google.com/").first()
#     print("Saved URL:", saved_url)
    
#     return f"<h1>Added URL</h1><p>{new_url.url}</p>"

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)