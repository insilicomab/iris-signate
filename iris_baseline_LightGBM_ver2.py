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

# object型の変数の取得
categories = train.columns[train.dtypes == 'object']
print(categories)

# 'class'のダミー変数化
le = LabelEncoder()
le = le.fit(train['class'])
train['class'] = le.transform(train['class'])

'''
モデルの構築と評価
'''

# ライブラリのインポート
import lightgbm as lgb
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from statistics import mean

# 5分割する
folds = 5
kf = KFold(n_splits=folds)

# ハイパーパラメータの設定
params = {
    # 多値分類問題
    'objective': 'multiclass',
    # クラス数は 3
    'num_class': 3
}

# 説明変数と目的変数を指定
X_train = train.drop(['class', 'id'], axis=1)
Y_train = train['class']

# 各foldごとに作成したモデルごとの予測値を保存
models = []
scores = []
oof = np.zeros(len(X_train))

for train_index, val_index in kf.split(X_train):
    x_train = X_train.iloc[train_index]
    x_valid = X_train.iloc[val_index]
    y_train = Y_train.iloc[train_index]
    y_valid = Y_train.iloc[val_index]
    
    lgb_train = lgb.Dataset(x_train, y_train)
    lgb_eval = lgb.Dataset(x_valid, y_valid, reference=lgb_train)    
    
    model = lgb.train(params,
                      lgb_train, 
                      valid_sets=lgb_eval, 
                      num_boost_round=100, # 学習回数の実行回数
                      early_stopping_rounds=20, # early_stoppingの判定基準
                      verbose_eval=10)
    
    y_pred = model.predict(x_valid, num_iteration=model.best_iteration)
    y_pred_max = np.argmax(y_pred, axis=1)  # 最尤と判断したクラスの値にする
    score = accuracy_score(y_valid, y_pred_max)
    print(score)
    
    models.append(model)
    scores.append(score)
    oof[val_index] = y_pred_max
    
    # 混同行列の作成
    cm = confusion_matrix(y_valid, y_pred_max)
    
    # heatmapによる混同行列の可視化
    sns.heatmap(cm, annot=True, cmap='Blues')
    plt.show()
    

# 平均accuracy scoreを計算する
print(mean(scores))


"""
予測精度：
0.9466666666666667
"""