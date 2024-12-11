# 머신러닝을 활용한 웹 피싱 탐지 서비스
### [제20회 한성공학경진대회 동상 수상]
**크롬 확장 프로그램**: [Catch Phishing Chrome Extension](https://chromewebstore.google.com/detail/catch-phishing/lcjnjlhedbbckkcenidmfokbpchnimji?hl=ko)  
**웹 사이트**: https://www.catch-phishing.site/

&nbsp;
## 작품 개요
최근 주요 웹 사이트를 모방한 피싱 사이트가 증가하면서 사용자를 유도하여 악성코들르 감염시키고, 개인정보와 금융 정보를 탈취하는 사이버 범죄가 빈번히 발생하고 있습니다.  
본 서비스는 **URL을 분석해 피싱 여부를 판별하는 머신너링 모델 XGBoos**t를 기반으로 **Chrome 확장 프로그램**과 **웹 애플리케이션**을 제공합니다.  
사용자는 이를 통해 **웹 사이트의 피싱 확률과 분석 결과를 실시간으로 확인**하고, 안전하게 웹을 탐색할 수 있습니다.
### 1. 투명한 탐지 근거 제공
- 피싱으로 판별된 이유와 해당 사이트의 상세 정보를 제공하여 분석 결과의 신뢰성과 이해도를 높임.

### 2. 사이트 접속 전 피싱 탐지
- **Chrome 확장 프로그램**: URL에 마우스를 올리기만 해도 피싱 여부를 미리 알려줌.  
- **웹 애플리케이션**: 사용자가 입력한 URL에 대해 피싱 여부를 사전에 탐지  

### 3. 정기적인 모델 업데이트
- 축적된 데이터베이스(DB)를 바탕으로 매달 정기적으로 모델을 업데이트해 탐지 정확도를 향상.

### 4. 신속한 응답
- 사전 학습된 모델의 예측과 블랙리스트를 활용해 사용자에게 즉각적인 피드백을 제공.

&nbsp;
## 주요 적용 기술
머신러닝 기반 피싱 사이트 탐지
- **XGBoost 모델**을 이용하여 복잡한 데이터 패턴을 학습해 정확하고 정밀한 피싱 사이트 탐지
- 테스트&사용 머신러닝 모델: **XGBoost**, **MLP**, **Random Forest**, **SVM**  

백엔드
- ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white)
- Flask를 확용하여 Python 기반의 경량 웹 프레임워크를 통해 실시간 탐지 API 제공
- AWS 클라우드를 이용하여 확장 가능하고 안전한 인프라를 통해 효율적인 데이터 처리 및 모델 배포
  
프론트엔드
- ![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat-square&logo=typescript&logoColor=white) ![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
- React 및 TypeScript를 활용하여 사용자 친화적이고 반응형 UI 사용  

확장 프로그램
- ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
- 사용자 편의를 위한 실시간 피싱 경고 서비스 제공

&nbsp;
## 데이터셋
사용 데이터셋: https://www.kaggle.com/datasets/akashkr/phishing-website-dataset
1. **중요도와 상관관계 분석**  
   - 피처 중요도 분석과 상관관계 분석을 통해 불필요한 피처를 제거.  
   - 주요 피처만 남겨 모델의 성능 평가를 진행.  

2. **과적합 방지**  
   - 학습 데이터에 지나치게 맞춰지는 것을 방지하여, 새로운 데이터에서도 일반화 성능을 유지.  
   - 이를 위해 적절한 피처 선택과 모델의 정규화 기법을 활용.  

3. **모델 단순화**  
   - 중요하지 않은 피처를 제거해 모델의 복잡도를 낮추고, 모델이 과적합되지 않도록 조정.  
   - 결과적으로 계산량이 줄어들어 학습 시간이 단축되고, 예측 속도가 향상됨.

![image](https://github.com/user-attachments/assets/0a3a3571-9ce0-49c8-9d27-d71b206edf45)
| ![image](https://github.com/user-attachments/assets/32e91651-fcbf-4889-89ee-635fda06b1c4) | ![image](https://github.com/user-attachments/assets/322524df-ad10-4025-9883-89dea85cd474) |
|---|---|

&nbsp;
## 피처 분류
URL 기반 피처, 도메인 기반 피처, 컨텐츠 기반 피처로 나누어 **피싱 여부를 정확히 판별**하여 높은 **정밀도**를 제공  

![image](https://github.com/user-attachments/assets/b35314a4-8e3d-4355-b8e9-46eab79dc3cb)


| ![image](https://github.com/user-attachments/assets/c62811db-ba10-4ed0-b557-5017001169c4) | ![image](https://github.com/user-attachments/assets/53133363-1984-43af-8963-21ededd2f857) |
|---|---|
| ![image](https://github.com/user-attachments/assets/a5b76677-7de6-420a-952b-cd66df472c2a) | ![image](https://github.com/user-attachments/assets/332cfa58-15d2-4939-8ea3-ee5290aff89b) |

&nbsp;
## 머신러닝
### 최종 선택 모델: **XGBoost**

### 성능 비교
- **XGBoost 테스트 정확도**: `0.9713`  
- **MLP 테스트 정확도**: `0.9765`

### 과적합 방지
- **XGBoost**는 트리 기반 모델로, 자체적인 과적합 방지 기법이 잘 적용되어 있음.  
- 훈련 데이터에서 매우 높은 정확도를 보이며, 교차 검증 결과 과적합이 발생하지 않았음을 확인.  

### 테스트 성능 차이
- **교차 검증 성능**과 **훈련 데이터의 혼동 행렬 분석**을 종합적으로 고려.  
- 높은 테스트 정확도와 적은 오탐률을 보이는 **XGBoost**를 최종 선정.

### 일관된 성능
- **교차 검증 평균 정확도**에서 XGBoost가 MLP보다 더 높은 성능을 보여, 새로운 데이터에서도 더 일관적인 성능을 보일 가능성이 큼.

![image](https://github.com/user-attachments/assets/04fad477-a2a3-4c10-806e-4f3c10d1fc4b)
![image](https://github.com/user-attachments/assets/7f0c868c-f78f-40d7-b8c6-03470e08c96f)
![image](https://github.com/user-attachments/assets/be5d31e8-98fb-4f10-b8ea-6d857ab51393)

## 확장 프로그램
URL을 실시간으로 분석하여 피싱 사이트로 의심될 경우 경고 메시지를 표시.  
사용자가 판별하고자 하는 웹 사이트의 **URL에 마우스 오버**할 때, **해당 URL이 피싱 사이트인지 아닌지를 즉시 판별**하여  
사용자는 매번 별도의 피싱 판별 웹 사이트를 방문하지 않고도 확장 프로그램을 통해 실시간으로 피싱 판별 결과를 받을 수 있어 편의성 향상  
<img width="916" alt="image" src="https://github.com/user-attachments/assets/01029b19-6274-49c6-8b55-5622065ea6e4">
| ![image](https://github.com/user-attachments/assets/d3b46861-c0fd-4211-abe4-b60fdbd56ee2) | ![image](https://github.com/user-attachments/assets/5f24a785-123d-483f-8130-a94096a8c261) |
|---|---|

**확장 프로그램**은 위와 같이 **활성화/비활성화** 버튼을 통해 사용자가 원하는 시점에 손쉽게 켜거나 끌 수 있어 사용자 편의성을 극대화.

&nbsp;
## 웹 사이트
확장 프로그램에서 자세히 보기를 클릭하면, 웹 사이트로 이동하여 피싱 판별 대상 웹 사이트의 **상세 정보**와 **피싱 판별 이유** 확인 가능  
또한, 웹 사이트에 직접 접속하여 **URL을 입력**하면 피싱 여부를 확인할 수 있으며,  
머신러닝 모델을 통해 판별된 **피싱 확률**과 **피싱 판별에 영향을 미친 주요 피처**들도 확인할 수 있어 이해도와 신뢰성을 높임.

![image](https://github.com/user-attachments/assets/d2bbc8cc-19f1-4eed-9c54-981189490e9b)

## 메인 화면
<img width="1256" alt="image" src="https://github.com/user-attachments/assets/03752ef6-07bc-40bb-a62e-ed077600ed2e">

## 정상 사이트의 경우
<img width="1259" alt="image" src="https://github.com/user-attachments/assets/471b6152-1ad5-4dc9-9e1c-29beaa8525cb"> 

정상 사이트로 판별될 경우, 머신러닝 모델을 통해 판별된 **피싱 확률** 과 **웹 사이트의 상세 정보** 제공

&nbsp;
## 피싱 사이트의 경우
<img width="1258" alt="image" src="https://github.com/user-attachments/assets/c6c39408-bc6e-4fb2-8f35-2606a8443cf9">  

피싱 사이트로 판별될 경우, 머신러닝 모델을 통해 분석된 **피싱 확률**, 웹 사이트의 **상세 정보**, **피싱 판별 이유에 해당하는 주요 피처 정보**를 제공

&nbsp;
## 프로젝트 흐름도  
<p align="center">
  <img width="500" alt="image" src="https://github.com/user-attachments/assets/9843f5f1-2ae5-42b7-acf5-ad010e604e34">
</p>

&nbsp;
## 서비스 아키텍처
![공경진 아키텍처](https://github.com/user-attachments/assets/17db24e4-e277-4cde-8fec-297e075f2cc7)
