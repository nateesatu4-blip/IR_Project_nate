
import warnings
warnings.filterwarnings("ignore")

from  New_Retrieval_Models import (
    es_model,
    tfidf_model,
    bm25_model,
    laplace_model,
    jm_model
)

# -----------------------------
# CONTROLS (CHANGE ONLY THESE)
# -----------------------------
QUERY_FILE = r"C:\Users\hp\Desktop\IR_Project_nate\Data\cran.qry"

MAX_QUERIES = 15    # LIMIT QUERIES
#MODEL = "tfidf"  
MODEL = "jm"    # CHANGE MODEL HERE ONLY

# -----------------------------
# LOAD QUERIES
# -----------------------------s
def parse_queries(file_path):
    queries = []
    qid, text = None, ""

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            if line.startswith(".I"):
                if qid is not None:
                    queries.append((qid, text.strip()))
                qid = int(line.split()[1])
                text = ""

            elif line.startswith(".W"):
                continue
            else:
                text += " " + line

        if qid is not None:
            queries.append((qid, text.strip()))

    return queries


# -----------------------------
# MAIN RUNNER
# -----------------------------
queries = parse_queries(QUERY_FILE)
queries = queries[:MAX_QUERIES]

results = {}

for qid, query in queries:
    print("Processing:", qid)

    if MODEL == "es":
        results[qid] = es_model(query)

    elif MODEL == "tfidf":
        results[qid] = tfidf_model(query)

    elif MODEL == "bm25":
        results[qid] = bm25_model(query)

    elif MODEL == "laplace":
        results[qid] = laplace_model(query)

    elif MODEL == "jm":
        results[qid] = jm_model(query)


# -----------------------------
# SAVE OUTPUT
# -----------------------------
""" def write_results(path, results):
    with open(path, "w") as f:
        for qid, docs in results.items():
            for rank, (doc, score) in enumerate(docs, 1):
                f.write(f"{qid} Q0 {doc} {rank} {score} Exp\n")


write_results(f"{MODEL}_results.txt", results)
 """
def write_results(path, results):
    with open(path, "w", encoding="utf-8") as f:
        for qid, docs in results.items():

            for rank, (doc, score) in enumerate(docs[:100], 1):  # TOP 100 ONLY

                f.write(f"{qid} Q0 {doc} {rank} {float(score)} Exp\n")


write_results(f"{MODEL}_results.txt", results)
print("DONE")























