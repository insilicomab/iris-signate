# -*- coding: utf-8 -*-

'''
データの読み込みと確認
'''

# ライブラリのインポート
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ランダムシードの設定
import random
np.random.seed(1234)
random.seed(1234)

# データの読み込み
train = pd.read_csv('./data/train.tsv', sep='\t')
test = pd.read_csv('./data/test.tsv', sep='\t')
submission = pd.read_csv('./data/sample_submit.csv')

# データの確認
print(train.head())
print(train.dtypes)

'''
特徴量エンジニアリング
'''

# ライブラリのインポート
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

# object型の変数の取得
categories = train.columns[train.dtypes == 'object']
print(categories)

# 'class'のダミー変数化
le = LabelEncoder()
le = le.fit(train['class'])
train['class'] = le.transform(train['class'])

# 説明変数と目的変数を指定
X_train = train.drop(['class', 'id'], axis=1)
Y_train = train['class']
X_test = test.drop(['id'], axis=1)

# 学習データとテストデータの説明変数の連結
X = pd.concat([X_train, X_test], sort=False).reset_index(drop=True)

# 説明変数の標準化
sc = StandardScaler()
sc.fit(X)
X_std = sc.transform(X)
X_std = pd.DataFrame(X_std)

# 標準化した説明変数を学習データとテストデータに分割
X_train_std = X_std[:len(train)]
X_test_std = X_std[len(train):]

'''
モデルの構築と評価
'''

# ライブラリのインポート
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from statistics import mean

# 5分割する
folds = 5
skf = StratifiedKFold(n_splits=folds)

# 各foldごとに作成したモデルごとの予測値を保存
models = []
scores = []
oof = np.zeros(len(X_train))

for train_index, val_index in skf.split(X_train_std, Y_train):
    x_train = X_train_std.iloc[train_index]
    x_valid = X_train_std.iloc[val_index]
    y_train = Y_train.iloc[train_index]
    y_valid = Y_train.iloc[val_index]
    
    clf = LogisticRegression()
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_valid)
    score = accuracy_score(y_valid, y_pred)
    print(score)
    
    models.append(clf)
    scores.append(score)
    oof[val_index] = y_pred
    
    # 混同行列の作成
    cm = confusion_matrix(y_valid, y_pred)
    
    # heatmapによる混同行列の可視化
    sns.heatmap(cm, annot=True, cmap='Blues')
    plt.show()
    
# 平均accuracy scoreを計算する
print(mean(scores))   
    
"""
予測精度：
0.9866666666666667
"""   

'''
テストデータの予測
'''

# ライブラリのインポート
from scipy import stats

# テストデータにおける予測
preds = []

for model in models:
    pred = model.predict(X_test_std)
    preds.append(pred)
    
# アンサンブル学習
preds_array = np.array(preds)
pred = stats.mode(preds_array)[0].T # 予測データリストのうち最頻値を算出し、行と列を入れ替え

'''
提出
'''

# 提出用データの読み込み
sub = pd.read_csv('./data/sample_submit.csv', sep=',', header=None)
print(sub.head())
    
# 目的変数カラムの置き換え
sub[1] = pred

# ダミー変数をもとの変数に戻す
sub[1] = sub[1].replace([0,1,2], ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica'])

# ファイルのエクスポート
sub.to_csv('./submit/iris_LogisticRegression.csv', header=None, index=None)    