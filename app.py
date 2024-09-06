from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
from config import DB_URL, DB_ENGINE_OPTIONS
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

db.init_app(app)

migrate = Migrate(app, db)

@app.route('/')
def index():
    return 'Hello World'

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
        b_response = {
            "url": input_url,
            "prediction_result": blacklist_info.b_result,
            "prediction_prob": f"{blacklist_info.b_prob}%"
        }
        return jsonify(b_response)

    # 블랙리스트에 없을 시 => 피처 추출/모델 예측/DB 저장 후, 결과 반환  
    simple_response_dto, features, prediction_result, prediction_prob = await url_service.simple_analyze_url(input_url) # 피처 추출, 모델 예측 

    # DB 저장
    url_entry = URLs.query.filter_by(url=input_url).first() # URLs에 있는지 검색

    if not url_entry:
        # URLs에 존재하지 않으면 새로 생성 후 DB 조작
        new_url_entry = URLs(url=input_url, search_count=1)
        db.session.add(new_url_entry)
        db.session.commit()
    
    feature_service.add_or_update_features_entity(db, input_url, features)
    predict_service.add_or_update_predictions(db, input_url, prediction_result, prediction_prob)

    blacklist_service.add_to_blacklist(db, url_entry) # search_count >= 20시, 블랙리스트 추가

    simple_response = {
        "url": input_url,
        "prediction_result": simple_response_dto.prediction_result,
        "prediction_prob": f"{simple_response_dto.prediction_prob}%"
    }
    return jsonify(simple_response)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
