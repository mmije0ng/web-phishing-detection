import pickle
import numpy as np
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from entity.models import Features, Predictions
from sqlalchemy import and_
from datetime import datetime


# 모델 평가 함수
def evaluate_model_accuracy(model, test_data, true_labels):
    """주어진 모델의 정확도를 계산"""
    predictions = model.predict(test_data)
    accuracy = accuracy_score(true_labels, predictions)
    return accuracy

# 새로운 모델 학습 및 비교 함수
def update_model_with_csv(db):
    """
    DB의 데이터와 dataset.csv 파일을 결합하여 모델을 재학습하고,
    기존 모델과 성능을 비교하여 더 나은 모델로 교체함.
    """
    print(f"Model update started at {datetime.now()}")

    # 기존 모델 로드
    with open('model/XGBoost_column_drop_model.pkl', 'rb') as f:
        current_xgboost_model = pickle.load(f)

    # 1. dataset.csv 파일 로드
    try:
        csv_data = pd.read_csv('dataset.csv', index_col=0) # 첫 번째 열(인덱스) 제거 후 불러옴
        # 특정 피처 드랍
        columns_to_drop = [
            'web_traffic',
            'Page_Rank',
            'Links_pointing_to_page',
            'Statistical_report',
            'Domain_registeration_length',
            'DNSRecord',
            'Abnormal_URL'
        ]
        csv_data = csv_data.drop(columns=columns_to_drop)

        csv_features = csv_data.drop(columns=['Result'])  # 피처 데이터
        csv_labels = csv_data['Result']  # 결과 데이터
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return

    # 2. DB에서 Features와 Predictions 테이블에서 데이터를 가져옴
    try:
        feature_entries = db.session.query(Features).all()
        prediction_entries = db.session.query(Predictions).all()

        # DB에서 피처와 라벨 배열 준비
        db_features = []
        db_labels = []

        for feature_entry in feature_entries:
            # 피처 배열 생성
            feature_values = [
                feature_entry.having_ip_address,
                feature_entry.url_length,
                feature_entry.shortening_service,
                feature_entry.having_at_symbol,
                feature_entry.double_slash_redirecting,
                feature_entry.prefix_suffix,
                feature_entry.having_sub_domain,
                feature_entry.ssl_final_state,
                feature_entry.favicon,
                feature_entry.port,
                feature_entry.https_token,
                feature_entry.request_url,
                feature_entry.url_of_anchor,
                feature_entry.links_in_tags,
                feature_entry.sfh,
                feature_entry.submitting_to_email,
                feature_entry.redirect,
                feature_entry.on_mouseover,
                feature_entry.right_click,
                feature_entry.popup_window,
                feature_entry.iframe,
                feature_entry.age_of_domain,
                feature_entry.google_index
            ]
            db_features.append(feature_values)

            # 해당 URL의 예측 결과 (라벨)를 가져옴
            prediction_entry = next((p for p in prediction_entries if p.url_id == feature_entry.url_id), None)
            if prediction_entry:
                db_labels.append(prediction_entry.prediction_result)

        # DB에서 가져온 데이터를 numpy 배열로 변환
        db_features = np.array(db_features)
        db_labels = np.array(db_labels)

    except Exception as e:
        print(f"Error retrieving data from DB: {e}")
        return

    # 3. dataset.csv 데이터와 DB 데이터를 결합
    combined_features = np.vstack((csv_features.values, db_features))
    combined_labels = np.hstack((csv_labels.values, db_labels))

    # 4. 학습용과 테스트용 데이터로 분리
    X_train, X_test, y_train, y_test = train_test_split(combined_features, combined_labels, test_size=0.3, random_state=42)

    # 5. 새로운 XGBoost 모델 학습
    new_xgboost_model = XGBClassifier()
    new_xgboost_model.fit(X_train, y_train)

    # 6. 기존 모델과 새로운 모델의 성능 비교
    current_xgboost_accuracy = evaluate_model_accuracy(current_xgboost_model, X_test, y_test)
    new_xgboost_accuracy = evaluate_model_accuracy(new_xgboost_model, X_test, y_test)

    if new_xgboost_accuracy > current_xgboost_accuracy:
        # 새 모델이 더 나은 성능을 보이면 모델 교체
        with open('model/XGBoost_column_drop_model.pkl', 'wb') as f:
            pickle.dump(new_xgboost_model, f)
        print(f"Model updated: {new_xgboost_accuracy:.4f} vs {current_xgboost_accuracy:.4f}")
    else:
        print(f"Model not updated: {new_xgboost_accuracy:.4f} <= {current_xgboost_accuracy:.4f}")

    print(f"Model update completed at {datetime.now()}")


# 스케줄러 설정
def schedule_model_update(db):
    """
    한 달에 한 번 모델을 업데이트하는 스케줄러 설정 함수
    """
    scheduler = BlockingScheduler()

    # 매달 1일 오전 2시에 모델 업데이트 실행
    scheduler.add_job(lambda: update_model_with_csv(db), 'cron', day=1, hour=2)

    print("Model update scheduler started.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Model update scheduler stopped.")