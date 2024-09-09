import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import seaborn as sns # pip install seaborn
import pickle

# 데이터 로드 및 준비
df = pd.read_csv('dataset.csv')
df = df.iloc[:, 1:]

X = df.drop(columns=['Result'])
y = df['Result']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLP 모델 인스턴스화
mlp = MLPClassifier(max_iter=1000, learning_rate_init=0.005, random_state=42)

# 모델 학습
mlp.fit(X_train, y_train)

# 교차 검증 수행
def exec_kfold(clf, folds=5):
    kfold = KFold(n_splits=folds)
    scores = []

    for iter_count, (train_index, test_index) in enumerate(kfold.split(X)):
        X_train_kf, X_test_kf = X.values[train_index], X.values[test_index]
        y_train_kf, y_test_kf = y.values[train_index], y.values[test_index]

        clf.fit(X_train_kf, y_train_kf)
        predictions = clf.predict(X_test_kf)
        accuracy = accuracy_score(y_test_kf, predictions)
        scores.append(accuracy)
        print(f"교차 검증 {iter_count} 정확도: {accuracy:.4f}")

    mean_score = np.mean(scores)
    print(f"평균 정확도: {mean_score:.4f}")

exec_kfold(mlp, folds=5)

# 모델 평가
y_train_pred = mlp.predict(X_train)
y_test_pred = mlp.predict(X_test)

train_accuracy = accuracy_score(y_train, y_train_pred)
test_accuracy = accuracy_score(y_test, y_test_pred)

train_report = classification_report(y_train, y_train_pred)
test_report = classification_report(y_test, y_test_pred)

print(f'훈련 정확도: {train_accuracy:.4f}')
print(f'테스트 정확도: {test_accuracy:.4f}')
print('훈련 분류 보고서:')
print(train_report)
print('테스트 분류 보고서:')
print(test_report)

# 혼동 행렬
cm_train = confusion_matrix(y_train, y_train_pred, labels=mlp.classes_)
disp_train = ConfusionMatrixDisplay(confusion_matrix=cm_train, display_labels=mlp.classes_)
disp_train.plot()
plt.show()

cm_test = confusion_matrix(y_test, y_test_pred, labels=mlp.classes_)
disp_test = ConfusionMatrixDisplay(confusion_matrix=cm_test, display_labels=mlp.classes_)
disp_test.plot()
plt.show()

# 하이퍼파라미터 튜닝
parameters = {
    'hidden_layer_sizes': [(100,), (50, 50), (100, 50)],
    'learning_rate_init': [0.001, 0.005, 0.01],
    'alpha': [0.0001, 0.001, 0.01],
}

grid_mlp = GridSearchCV(mlp, param_grid=parameters, scoring='accuracy', n_jobs=-1, cv=5)
grid_mlp.fit(X_train, y_train)

print('GridSearchCV 최적 하이퍼 파라미터 :', grid_mlp.best_params_)
print('GridSearchCV 최고 정확도: {0:.4f}'.format(grid_mlp.best_score_))

# 최적 모델 평가
best_mlp = grid_mlp.best_estimator_
dpredictions = best_mlp.predict(X_test)
accuracy = accuracy_score(y_test, dpredictions)
print('테스트 세트에서의 최적 MLP 정확도 : {0:.4f}'.format(accuracy))