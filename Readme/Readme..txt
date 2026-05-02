Information Retrieval Project
Overview
This project implements and evaluates multiple Information Retrieval (IR) models using the Cranfield dataset. The goal is to compare different ranking strategies and analyze their effectiveness in retrieving relevant documents.
Models Implemented
* Elasticsearch Built-in (BM25-based)
* TF-IDF
* BM25
* Language Model (Laplace Smoothing)
* Language Model (Jelinek-Mercer Smoothing)
System Workflow
Query → Elasticsearch → Candidate Retrieval → Feature Extraction → Scoring → Ranking → Output → Evaluation
Tools and Technologies
* Python
* Elasticsearch
* trec_eval
Evaluation
The system was evaluated using trec_eval with the following metrics:
* Mean Average Precision (MAP)
* Precision@10 (P@10)
* Reciprocal Rank
* R-Precision
Sample Results
Model
	MAP
	P@10
	ES Built-in
	0.3238
	0.2067
	TF-IDF
	0.2427
	0.1600
	BM25
	0.2350
	0.1667
	JM
	0.2149
	0.1533
	Laplace
	0.0646
	0.0667
	How to Run
1. Start Elasticsearch
2. Index the dataset: with file name “New_indexing.py
      3.Run query processing: with “New_Query_processing.py” and  “New_Retrieval_models.py
      4.Evaluate results:

Notes
* Limited queries and document sizes were used for efficiency during development.
* Results are generated in TREC format.