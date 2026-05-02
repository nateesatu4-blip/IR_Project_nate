from elasticsearch import Elasticsearch
import math

# -----------------------------
# CONNECTION
# -----------------------------
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "8ayvY0PoHKqHlx2WrC5i"),
    verify_certs=False
)

INDEX = "cranfield_index"

# -----------------------------
# GLOBAL LIMITS (SAFE MODE)
# -----------------------------
ES_SIZE = 1390  # docs per query (LIMIT)
TOP_K = 100    # final output size
LAMBDA = 0.8   # JM smoothing
V = 10000      # vocab estimate

# -----------------------------
# HELPERS (FAST + SAFE)
# -----------------------------
def get_candidates(query):
    return es.search(
        index=INDEX,
        size=ES_SIZE,
        query={"match": {"text": query}}
    )["hits"]["hits"]


def get_tf(term, text):
    return text.split().count(term)


def get_doc_len(text):
    return len(text.split())


def get_df(term):
    return es.count(
        index=INDEX,
        query={"match": {"text": term}}
    )["count"]


def avg_doc_len():
    res = es.search(index=INDEX, size=ES_SIZE, query={"match_all": {}})
    docs = [len(h["_source"]["text"].split()) for h in res["hits"]["hits"]]
    return sum(docs) / max(len(docs), 1)


# cached global value (IMPORTANT FOR SPEED)
AVG_LEN = avg_doc_len()
D = es.count(index=INDEX)["count"]

# =========================================================
# 1. ES BUILT-IN MODEL
# =========================================================
def es_model(query):
    res = es.search(
        index=INDEX,
        size=ES_SIZE,
        query={"match": {"text": query}}
    )

    return [(h["_id"], h["_score"]) for h in res["hits"]["hits"]]


# =========================================================
# 2. TF-IDF
# =========================================================
def tfidf_model(query):
    results = {}
    terms = query.lower().split()

    for hit in get_candidates(query):
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()

        score = 0
        for t in terms:
            tf = get_tf(t, text)
            if tf == 0:
                continue

            df = get_df(t)
            if df == 0:
                continue

            ok_tf = tf / (tf + 0.5 + 1.5 * (len(text.split()) / AVG_LEN))
            idf = math.log10(D / df)

            score += ok_tf * idf

        if score > 0:
            results[doc_id] = score

    return sorted(results.items(), key=lambda x: x[1], reverse=True)[:TOP_K]


# =========================================================
# 3. BM25
# =========================================================
def bm25_model(query):
    results = {}
    k1, b = 1.2, 0.75
    terms = query.lower().split()

    for hit in get_candidates(query):
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()
        dl = len(text.split())

        score = 0
        for t in terms:
            tf = get_tf(t, text)
            if tf == 0:
                continue

            df = get_df(t)
            if df == 0:
                continue

            idf = math.log10((D + 0.5) / (df + 0.5))
            denom = tf + k1 * ((1 - b) + b * dl / AVG_LEN)

            score += idf * ((tf * (k1 + 1)) / denom)

        if score > 0:
            results[doc_id] = score

    return sorted(results.items(), key=lambda x: x[1], reverse=True)[:TOP_K]


# =========================================================
# 4. LAPLACE LM
# =========================================================
def laplace_model(query):
    results = {}

    for hit in get_candidates(query):
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()
        dl = len(text.split())

        score = 0
        for t in query.lower().split():
            tf = get_tf(t, text)
            prob = (tf + 1) / (dl + V)
            score += math.log(prob)

        results[doc_id] = score

    return sorted(results.items(), key=lambda x: x[1], reverse=True)[:TOP_K]


# =========================================================
# 5. JELINEK-MERCER LM
# =========================================================
def jm_model(query):
    results = {}

    for hit in get_candidates(query):
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()
        dl = len(text.split())

        score = 0
        for t in query.lower().split():
            tf = get_tf(t, text)
            p_doc = tf / dl if dl > 0 else 0
            p_coll = 1 / V

            prob = LAMBDA * p_doc + (1 - LAMBDA) * p_coll
            score += math.log(prob)

        results[doc_id] = score

    return sorted(results.items(), key=lambda x: x[1], reverse=True)[:TOP_K]

















































""" 
from elasticsearch import Elasticsearch
import math

# -----------------------------
# 1. Connect to Elasticsearch
# -----------------------------
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "8ayvY0PoHKqHlx2WrC5i"),
    verify_certs=False
)

INDEX = "cranfield_index"

# -----------------------------
# 2. Global values
# -----------------------------
D = es.count(index=INDEX)["count"]


# -----------------------------
# 3. Helper Functions
# -----------------------------

def get_candidates(query):
    res = es.search(
        index=INDEX,
        size=1000,
        query={"match": {"text": query}}
    )
    return res["hits"]["hits"]


def get_tf(term, text):
    return text.split().count(term)


def get_doc_len(text):
    return len(text.split())


def get_df(term):
    res = es.count(
        index=INDEX,
        query={"match": {"text": term}}
    )
    return res["count"]


def get_avg_doc_len():
    res = es.search(index=INDEX, size=1000, query={"match_all": {}})
    lengths = [len(hit["_source"]["text"].split()) for hit in res["hits"]["hits"]]
    return sum(lengths) / len(lengths)


# -----------------------------
# 4. TF-IDF MODEL
# -----------------------------
def tfidf_model(query):
    avg_len = get_avg_doc_len()
    candidates = get_candidates(query)
    scores = {}

    terms = query.lower().split()

    for hit in candidates:
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()
        doc_len = get_doc_len(text)

        score = 0

        for term in terms:
            tf = get_tf(term, text)
            if tf == 0:
                continue

            df = get_df(term)
            if df == 0:
                continue

            ok_tf = tf / (tf + 0.5 + 1.5 * (doc_len / avg_len))
            idf = math.log10(D / df)

            score += ok_tf * idf

        if score > 0:
            scores[doc_id] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:100]


# -----------------------------
# 5. BM25 MODEL
# -----------------------------
def bm25_model(query):
    avg_len = get_avg_doc_len()
    candidates = get_candidates(query)
    scores = {}

    k1 = 1.2
    b = 0.75

    terms = query.lower().split()

    for hit in candidates:
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()
        doc_len = get_doc_len(text)

        score = 0

        for term in terms:
            tf = get_tf(term, text)
            if tf == 0:
                continue

            df = get_df(term)
            if df == 0:
                continue

            idf = math.log10((D + 0.5) / (df + 0.5))
            denom = tf + k1 * ((1 - b) + b * (doc_len / avg_len))
            score += idf * ((tf * (k1 + 1)) / denom)

        if score > 0:
            scores[doc_id] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:100]


# -----------------------------
# 6. LAPLACE MODEL
# -----------------------------
def laplace_model(query):
    candidates = get_candidates(query)
    scores = {}

    V = 10000  # approximate vocabulary size

    terms = query.lower().split()

    for hit in candidates:
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()
        doc_len = get_doc_len(text)

        score = 0

        for term in terms:
            tf = get_tf(term, text)
            prob = (tf + 1) / (doc_len + V)
            score += math.log(prob)

        scores[doc_id] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:100]


# -----------------------------
# 7. JELINEK-MERCER MODEL
# -----------------------------
def jm_model(query):
    candidates = get_candidates(query)
    scores = {}

    lam = 0.8
    V = 10000  # approximate

    terms = query.lower().split()

    for hit in candidates:
        doc_id = hit["_id"]
        text = hit["_source"]["text"].lower()
        doc_len = get_doc_len(text)

        score = 0

        for term in terms:
            tf = get_tf(term, text)
            p_doc = tf / doc_len if doc_len > 0 else 0
            p_coll = 1 / V

            prob = lam * p_doc + (1 - lam) * p_coll
            score += math.log(prob)

        scores[doc_id] = score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:100] 
    
 """
