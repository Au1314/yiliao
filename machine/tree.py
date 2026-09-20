"""病情分类模型：jieba 分词 + TF-IDF + 随机森林。

- 训练后将模型与 vectorizer 用 joblib 持久化到本目录（model.pkl / vectorizer.pkl）
- predict() 供 app.py 调用，模型不存在时自动训练
"""
import os
import sys

import jieba
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# 保证能 import 项目根目录下的 config 与 utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.query import querys  # noqa: E402

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
STOPWORD_PATH = os.path.join(MODEL_DIR, "stopword.txt")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

MAX_FEATURES = 10000
N_ESTIMATORS = 100


def _load_stopwords():
    with open(STOPWORD_PATH, "r", encoding="utf-8") as f:
        return set(f.read().splitlines())


_STOPWORDS = _load_stopwords()


def tokensize(text):
    words = [w for w in jieba.cut(str(text)) if w.strip() and w not in _STOPWORDS]
    return " ".join(words)


def get_data():
    rows = querys("select content, type from cases", [], "select")
    df = pd.DataFrame(rows, columns=["content", "type"])
    df["content"] = df["content"].apply(tokensize)
    return df


def train_and_save():
    data = get_data()
    x_train, x_test, y_train, y_test = train_test_split(
        data["content"], data["type"], test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(max_features=MAX_FEATURES)
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    model = RandomForestClassifier(n_estimators=N_ESTIMATORS, random_state=42)
    model.fit(x_train_vec, y_train)
    y_pred = model.predict(x_test_vec)
    accuracy = accuracy_score(y_test, y_pred)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    return accuracy


def _load_or_train():
    """加载已保存的模型；不存在则训练并保存。返回 (model, vectorizer)。"""
    if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
        return joblib.load(MODEL_PATH), joblib.load(VECTORIZER_PATH)
    train_and_save()
    return joblib.load(MODEL_PATH), joblib.load(VECTORIZER_PATH)


_model, _vectorizer = None, None


def predict(content):
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        _model, _vectorizer = _load_or_train()
    tokens = tokensize(content)
    vec = _vectorizer.transform([tokens])
    return _model.predict(vec)[0]


def predict_with_proba(content, k=3):
    """预测病情，返回 top-k 疾病及其概率 [(疾病, 概率), ...]，概率为 0~1 浮点。"""
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        _model, _vectorizer = _load_or_train()
    tokens = tokensize(content)
    vec = _vectorizer.transform([tokens])
    proba = _model.predict_proba(vec)[0]
    order = proba.argsort()[::-1][:k]
    return [(str(_model.classes_[i]), round(float(proba[i]), 4)) for i in order]


if __name__ == "__main__":
    acc = train_and_save()
    print("训练完成，测试集准确率:", acc)
    print("示例预测(腰部疼痛):", predict("腰部疼痛"))
