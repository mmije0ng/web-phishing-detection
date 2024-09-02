from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

# URL 정보
class URLs(db.Model):
    __tablename__ = 'URLs'  # 테이블 이름을 'URLs'로 지정

    url_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # pk
    url = db.Column(db.String(255), nullable=False, unique=True)
    is_blacklisted = db.Column(db.Boolean, default=False) # 블랙리스트 여부
    search_count = db.Column(db.Integer, default=0) # URL 조회 횟수
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    predictions = db.relationship('Predictions', back_populates='url', cascade='all, delete-orphan')
    blacklist = db.relationship('Blacklist', back_populates='url', uselist=False, cascade='all, delete-orphan')
    features = db.relationship('Features', back_populates='url', uselist=False, cascade='all, delete-orphan')

# 피싱 탐지 결과
class Predictions(db.Model):
    __tablename__ = 'Predictions'  # 테이블 이름을 'Predictions'로 지정

    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # pk
    url_id = db.Column(db.Integer, db.ForeignKey('URLs.url_id'), nullable=False) # fk
    prediction_result = db.Column(db.SmallInteger) # 분석 결과
    prediction_prob = db.Column(db.Float) # 피싱 확률
    predicted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow) 

    # Relationships
    url = db.relationship('URLs', back_populates='predictions')

# 블랙리스트 테이블
# 자주 검색되거나 중요한 URL을 저장하여 응답 속도 개선
class Blacklist(db.Model):
    __tablename__ = 'Blacklist'  # 테이블 이름을 'Blacklist'로 지정

    blacklist_id = db.Column(db.Integer, primary_key=True, autoincrement=True) # pk
    url_id = db.Column(db.Integer, db.ForeignKey('URLs.url_id'), nullable=False) # fk
    b_result = db.Column(db.SmallInteger) # 분석 결과
    b_prob = db.Column(db.Float) # 피싱 확률
    blacklisted_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    url = db.relationship('URLs', back_populates='blacklist')

# URL의 피처 값을 관리 & 모델 학습에 사용
class Features(db.Model):
    __tablename__ = 'Features'  # 테이블 이름을 'Features'로 지정

    url_id = db.Column(db.Integer, db.ForeignKey('URLs.url_id'), primary_key=True)  # ForeignKey 참조 변경
    having_ip_address = db.Column(db.SmallInteger)
    url_length = db.Column(db.SmallInteger)
    shortening_service = db.Column(db.SmallInteger)
    having_at_symbol = db.Column(db.SmallInteger)
    double_slash_redirecting = db.Column(db.SmallInteger)
    prefix_suffix = db.Column(db.SmallInteger)
    having_sub_domain = db.Column(db.SmallInteger)
    ssl_final_state = db.Column(db.SmallInteger)
    favicon = db.Column(db.SmallInteger)
    port = db.Column(db.SmallInteger)
    https_token = db.Column(db.SmallInteger)
    request_url = db.Column(db.SmallInteger)
    url_of_anchor = db.Column(db.SmallInteger)
    links_in_tags = db.Column(db.SmallInteger)
    sfh = db.Column(db.SmallInteger)
    submitting_to_email = db.Column(db.SmallInteger)
    redirect = db.Column(db.SmallInteger)
    on_mouseover = db.Column(db.SmallInteger)
    right_click = db.Column(db.SmallInteger)
    popup_window = db.Column(db.SmallInteger)
    iframe = db.Column(db.SmallInteger)
    age_of_domain = db.Column(db.SmallInteger)
    google_index = db.Column(db.SmallInteger)

    # Relationships
    url = db.relationship('URLs', back_populates='features')