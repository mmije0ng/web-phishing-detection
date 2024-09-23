from entity.models import URLs, Blacklist, Predictions

# 블랙리스트 확인
def check_blacklist(db, input_url):
    # URLs 테이블에서 URL이 블랙리스트에 있는지 확인
    url_entry = URLs.query.filter_by(url=input_url).first()

    # URL이 존재하고, 블랙리스트에 등록된 경우
    if url_entry and url_entry.is_blacklisted:
        # search_count 증가
        url_entry.search_count += 1
        db.session.commit()

        # Blacklist 테이블에서 블랙리스트 정보 가져오기
        blacklist_entry = Blacklist.query.filter_by(url_id=url_entry.url_id).first()
        return blacklist_entry
    
    return None

# 블랙리스트 추가 
def add_to_blacklist(db, url):
    url_entry = URLs.query.filter_by(url=url).first()
    if url_entry.search_count >= 20:
        prediction_entry = Predictions.query.filter_by(url_id=url_entry.url_id).first()

        #if prediction_entry and prediction_entry.prediction_result == 1:
        if prediction_entry:
            # 블랙리스트에 추가
            new_blacklist_entry = Blacklist(
                url_id=url_entry.url_id, 
                b_result=prediction_entry.prediction_result, 
                b_prob=prediction_entry.prediction_prob
            )
            db.session.add(new_blacklist_entry)

            # URLs 테이블에서 is_blacklisted를 True로 업데이트
            url_entry.is_blacklisted = True
            db.session.commit()

            print(f"URL {url_entry.url} : 블랙리스트에 추가되었습니다.")
        else:
            print("블랙리스트에 추가할 수 없습니다. Predictions 테이블에 해당 데이터가 존재하지 않습니다.")


# predictions 테이블 기반으로 blacklist 테이블 최신화 (업데이트)
def update_blacklist(db, input_url_id, prediction_result, prediction_prob):
    try:
        # URL이 블랙리스트에 있는지 확인
        url_entry = URLs.query.filter_by(url_id=input_url_id).first()
        if url_entry and url_entry.is_blacklisted:
            blacklist_entry = Blacklist.query.filter_by(url_id=input_url_id).first()
            if blacklist_entry:
                # 기존 블랙리스트 레코드 업데이트
                blacklist_entry.b_result = prediction_result
                blacklist_entry.b_prob = prediction_prob
                print(f"Blacklist updated for URL ID {input_url_id}")
            else:
                print(f"Blacklist에서 URL ID:{input_url_id}의 레코드를 찾을 수 없습니다.")
            # 데이터베이스에 커밋
            db.session.commit()

    except Exception as e:
        # 에러 발생 시 롤백 및 로그 출력
        db.session.rollback()
        print(f"Error updating blacklist for URL ID {input_url_id}: {e}")
