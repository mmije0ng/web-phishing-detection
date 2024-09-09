from flask import Flask, request, jsonify
from flask_cors import CORS # pip install flask-cors
#from aioflask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from config import DB_URL, DB_ENGINE_OPTIONS
from entity.models import db, URLs
from service import url_service
from entity.models import db, URLs, Predictions, Features, Blacklist
from service import url_service, feature_service, predict_service, blacklist_service

app = Flask(__name__)

# CORS 설정
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}},
    allow_headers="*", expose_headers="*", supports_credentials=True, max_age=3600)

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

# (확장용) 피싱 여부 및 확률
@app.route('/api/url/simple', methods=['POST'])
async def simple_result():
    data = request.get_json()
    input_url = data.get('url')

    if not input_url:
        return {"error": "No URL provided"}, 400  # URL이 없으면 400 Bad Request 반환

    # 블랙리스트 검색
    blacklist_info = blacklist_service.check_blacklist(db, input_url)

    # 블랙리스트에 있을 시 => 바로 결과 반환
    if blacklist_info:
        # DB에서 예측 결과 가져오기
        print("########바로 반환###########")
        b_response = {
            "url": input_url,
            "prediction_result": blacklist_info.b_result,
            "prediction_prob": f"{blacklist_info.b_prob}%"
        }
        return jsonify(b_response)

    # 블랙리스트에 없을 시 => 피처 추출/모델 예측/DB 저장 후, 결과 반환  
    simple_response_dto = await url_service.simple_analyze_url(db, input_url) # 피처 추출, 모델 예측 

    # 해당 내용 simple_analyze_url 내부로 옮김 
    # DB 저장 
    # url_entry = URLs.query.filter_by(url=input_url).first() # URLs에 있는지 검색

    # if not url_entry:
    #     # URLs에 존재하지 않으면 새로 생성 후 DB 조작
    #     new_url_entry = URLs(url=input_url, search_count=1)
    #     db.session.add(new_url_entry)
    #     db.session.commit()
    
    # feature_service.add_or_update_features_entity(db, input_url, features)
    # predict_service.add_or_update_predictions(db, input_url, prediction_result, prediction_prob)

    # blacklist_service.add_to_blacklist(db, url_entry) # search_count >= 20시, 블랙리스트 추가

    simple_response = {
        "url": input_url,
        "prediction_result": simple_response_dto.get('prediction_result'),
        "prediction_prob": f"{simple_response_dto.get('prediction_prob')}"
    }
    return jsonify(simple_response)


# (웹용) 피싱 분석 상세 결과
@app.route('/api/url/detailed', methods=['POST'])
async def detailed_result():
    # request body에서 JSON 데이터를 가져옴
    url = request.get_json().get('url')

    if not url:
        return {"error": "No URL provided"}, 400  # URL이 없으면 400 Bad Request 반환

    # Blacklist 검색 로직
    # Blacklist 있을 시 db 검색

    # Blacklist 없을 시 feature 추출, 모델 예측, db
    detailed_response_dto = await url_service.detailed_analyze_url(db, url)

    # 분석 결과 반환
    return jsonify(detailed_response_dto)


# # 데이터베이스 연결 테스트
# @app.route('/test-connection')
# def test_connection():
#     try:
#         with db.engine.connect() as connection:
#             # SQLAlchemy의 text 객체를 사용하여 쿼리 실행
#             # 간단한 쿼리를 실행하여 연결 확인
#             result = connection.execute(text("SELECT 1"))
#             return "Database connection successful"
#     except Exception as e:
#         return f"Database connection failed: {e}"

    
# # db 데이터 create test
# @app.route('/test')
# def add_url():
#     # URL 객체 생성 및 데이터베이스에 추가
#     new_url = URLs(url="https://www.notion.so/f267366bd61041c88f7bb39edddf46bc")
#     db.session.add(new_url)
    
#     # 세션에 데이터가 있는지 확인
#     print("Session pending changes:", db.session.new)
    
#     # 데이터베이스에 커밋
#     db.session.commit()
    
#     # 커밋 후 데이터가 있는지 확인
#     saved_url = URLs.query.filter_by(url="https://www.notion.so/f267366bd61041c88f7bb39edddf46bc").first()
#     print("Saved URL:", saved_url)
    
#     return f"<h1>Added URL</h1><p>{new_url.url}</p>"


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)