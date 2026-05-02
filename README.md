Information Retrieval Project
Overview  

This project implements and evaluates multiple Information Retrieval (IR) models using the Cranfield dataset. The goal is to compare different ranking strategies and analyze their effectiveness in retrieving relevant documents.

Models Implemented
Elasticsearch Built-in (BM25-based),
TF-IDF,
BM25,
Language Model (Laplace Smoothing),
Language Model (Jelinek-Mercer Smoothing)

System Workflow 
Query → Elasticsearch → Candidate Retrieval → Feature Extraction → Scoring → Ranking → Output → Evaluation

Tools and Technologies
Python,
Elasticsearch,
trec_eval Evaluation

The system was evaluated using trec_eval with the following metrics:
Mean Average Precision (MAP),
Precision@10 (P@10),
Reciprocal Rank, 
R-Precision


Start Elasticsearch 
Index the dataset: with file name “New_indexing.py
      3.Run query processing: with “New_Query_processing.py” and  “New_Retrieval_models.py
       4.Evaluate results:


Notes : 
Limited queries and document sizes were used for efficiency during development. , 
Results are generated in TREC format.

