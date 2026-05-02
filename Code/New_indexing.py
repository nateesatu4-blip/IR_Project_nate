import os
import time
from elasticsearch import Elasticsearch

# -----------------------------
# 1. Connect to Elasticsearch
# -----------------------------
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "8ayvY0PoHKqHlx2WrC5i"),
    verify_certs=False
)

print(es.info())

# -----------------------------
# 2. Dataset path
# -----------------------------
path = r"C:\Users\hp\Desktop\IR_Project_nate\Data\cran.all.1400"

start_time = time.time()
doc_count = 0


# -----------------------------
# 3. Parse Cranfield format
# -----------------------------
def parse_documents(file_content):
    """
    Splits raw Cranfield file into structured documents
    """
    raw_docs = file_content.split(".I ")[1:]  # each document starts here

    documents = []

    for raw_doc in raw_docs:
        lines = raw_doc.splitlines()

        doc_id = lines[0].strip()

        title = ""
        author = ""
        bib = ""
        text = ""

        current_section = None

        for line in lines[1:]:
            line = line.strip()

            if line == ".T":
                current_section = "title"
                continue
            elif line == ".A":
                current_section = "author"
                continue
            elif line == ".B":
                current_section = "bib"
                continue
            elif line == ".W":
                current_section = "text"
                continue

            # Append content to correct section
            if current_section == "title":
                title += line + " "
            elif current_section == "author":
                author += line + " "
            elif current_section == "bib":
                bib += line + " "
            elif current_section == "text":
                text += line + " "

        documents.append({
            "doc_id": doc_id,
            "title": title.strip(),
            "author": author.strip(),
            "bib": bib.strip(),
            "text": text.strip()
        })

    return documents


# -----------------------------
# 4. Index documents
# -----------------------------
# -----------------------------
# Read single dataset file
# -----------------------------

# -----------------------------
# Read dataset (SINGLE FILE)
# -----------------------------
with open(path, "r", encoding="utf-8", errors="ignore") as file:
    content = file.read()

docs = parse_documents(content)

# -----------------------------
# Index documents
# -----------------------------
for doc in docs:
    doc_count += 1

    es.index(
        index="cranfield_index",
        id=doc["doc_id"],
        body={
            "title": doc["title"],
            "author": doc["author"],
            "bib": doc["bib"],
            "text": doc["text"]
        }
    )

    print(f"Indexed document {doc_count}: {doc['doc_id']}")


# -----------------------------
# 5. Execution time
# -----------------------------
end_time = time.time()
total = end_time - start_time

hours = int(total // 3600)
minutes = int((total % 3600) // 60)
seconds = int(total % 60)

print("\nIndexing completed!")
print(f"Total documents indexed: {doc_count}")
print(f"Time taken: {hours}:{minutes}:{seconds}")