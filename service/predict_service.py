import pickle
from entity.models import Predictions

# 피싱 여부 및 확률 예측 함수
from service.blacklist_service import update_blacklist

# 피싱 여부 및 확률 예측 함수
def predict_phishing(features_array):
    """피처 배열을 입력받아 피싱 여부와 확률을 반환하는 함수."""
    
    # 학습된 XGBoost 모델 로드
    with open('model/XGBoost_column_drop_model.pkl', 'rb') as f:
        xgboost_model = pickle.load(f)

    # XGBoost 모델 예측
    prediction_result = xgboost_model.predict(features_array)[0]  # 피싱 여부
    xgboost_probability = xgboost_model.predict_proba(features_array)[0]  # 모델 예측 확률
    prediction_prob = round(xgboost_probability[1] * 100, 4)  # 피싱일 확률을 퍼센트로 변환하고 소수점 네 자리로 반올림

    # prediction_result가 1이 아닌 경우 -1 반환
    if prediction_result != 1:
        prediction_result = -1

    return prediction_result, prediction_prob


# Predictions 테이블에 예측 결과를 저장하거나 업데이트하는 함수
def add_or_update_predictions(db, url_id, prediction_result, prediction_prob):
    try:
        # 예측 결과 로그 출력
        print('prediction result: ' + str(prediction_result))
        print('prediction prob: ' + str(prediction_prob))

        # numpy.int32 타입을 Python의 기본 int 타입으로 변환
        prediction_result = int(prediction_result)
        prediction_prob = float(prediction_prob)

        # 기존 Predictions가 있는지 확인
        prediction_entity = Predictions.query.filter_by(url_id=url_id).first()

        if prediction_entity:
            # 기존 레코드가 있을 경우 업데이트
            prediction_entity.prediction_result = prediction_result
            prediction_entity.prediction_prob = prediction_prob
            print(f"Prediction updated for URL ID {url_id}")
            # 업데이트된 경우 Blacklist 테이블도 업데이트 (b_result, b_prob)
            update_blacklist(db, url_id, prediction_result, prediction_prob)

        else:
            # 레코드가 없을 경우 새로 추가
            new_prediction_entity = Predictions(
                url_id=url_id,
                prediction_result=prediction_result,  # 피싱 여부
                prediction_prob=prediction_prob,  # 피싱 확률
            )
            db.session.add(new_prediction_entity)
            print(f"New prediction added for URL ID {url_id}")

        # 데이터베이스에 커밋
        db.session.commit()

    except Exception as e:
        # 에러 발생 시 롤백 및 로그 출력
        db.session.rollback()
        print(f"Error saving or updating prediction for URL ID {url_id}: {e}")


# # Predictions 테이블의 피싱 여부 및 확률 업데이트
# def update_predictions_entity(db, url_id, prediction_result, prediction_prob):
#     print('prediction result: '+str(prediction_result))
#     print('prediction prob: '+str(prediction_prob))
    
#     # 기존 Predictions가 있는지 확인


#     prediction_entity = Predictions.query.filter_by(url_id=url_id).first()

#     prediction_entity.prediction_result = prediction_result
#     prediction_entity.prediction_prob = prediction_prob

#     # 데이터베이스에 커밋
#     db.session.commit()

#     print(f"Prediction updated for URL ID {url_id}")


# # Predictions 테이블에 예측 결과를 저장하는 함수
# def add_predictions_entity(db, url_id, prediction_result, prediction_prob):
#     # 예측 결과 저장
#     new_prediction_entity = Predictions(
#         url_id=url_id,
#         prediction_result=prediction_result,  # 피싱 여부
#         prediction_prob=prediction_prob,  # 피싱 확률
#     )

#     db.session.add(new_prediction_entity)

#     # 데이터베이스에 커밋
#     db.session.commit()

#     print(f"New prediction added for URL ID {url_id}")

