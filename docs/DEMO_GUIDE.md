# 10-Minute Video Demonstration & Presentation Script
## Yelp Big Data Analytics & Temporal Quality Forecasting Pipeline

This guide provides a structured, minute-by-minute blueprint for recording or presenting a **10-minute video demo** of the complete Big Data pipeline.

---

## Timetable & Phase Overview

| Time Interval | Section Title | Target Screen / Visual | Key Talking Points |
|---|---|---|---|
| **0:00 – 1:00** | Project Overview & Problem Statement | `README.md` & Architecture Diagram | Scale (5.1 GB, 7M reviews), semi-structured data challenges, temporal data leakage in ML. |
| **1:00 – 2:30** | Data Ingestion & Pig ETL with Java UDFs | Terminal / HDFS listing & Java UDF code | HDFS storage (`/yelp_project/raw/`), Pig EvalFunc UDFs stripping `\r\n\t`, tab-delimited output. |
| **2:30 – 4:00** | Hive Data Warehousing & OLAP Analytics | Terminal / Hive DDL & Query Results | Schema-on-read, external tables, state aggregations, category explosion, popularity vs quality. |
| **4:00 – 5:30** | PySpark NLP & Aspect Sentiment Mining | `spark/business_quality_analysis.py` | Tokenization, StopWordsRemover, CountVectorizer, 8-dimensional aspect mining (14.8M mentions). |
| **5:30 – 7:15** | Out-of-Time Forecasting (Spark MLlib) | `spark/business_quality_prediction.py` | Avoiding lookahead bias: consecutive-year pairs ($t \to t+1$), strict temporal split, Random Forest. |
| **7:15 – 8:45** | Key Results & Visual Analytics | `visualizations/*.png` (Charts 1, 3, 6, 7, 8, 11) | Rating distribution, California vs Delaware, confusion matrix (46.83% acc, 0.4660 F1), scatter plot. |
| **8:45 – 9:30** | Limitations & Architectural Tradeoffs | `docs/FINAL_REPORT.md` (Sections 9 & 10) | Survivorship bias, regex dictionary vs BERT, single-node metastore, future streaming roadmap. |
| **9:30 – 10:00** | Conclusion & Deliverables Summary | Repository root & Verification checklist | End-to-end pipeline success, reproducibility, artifact verification. |

---

## Detailed Minute-by-Minute Script & Action Guide

### [0:00 – 1:00] Introduction & Problem Formulation
- **Screen Action**: Display the top of `README.md` and scroll to the **Architecture & System Flow** diagram.
- **Spoken Script**:
  > *"Hello everyone. Today I'm presenting our end-to-end Big Data Analytics and Temporal Business Quality Forecasting Pipeline built on the Yelp Academic Dataset.*  
  > *Our dataset contains over 5.1 gigabytes of semi-structured JSON records, encompassing 150,346 commercial entities and nearly 7 million customer reviews.*  
  > *In real-world big data engineering, three major challenges arise: first, handling messy multiline text with unescaped carriage returns and tabs that corrupt standard data warehouses; second, uncovering whether high review popularity actually reflects quality; and third, predicting future business rating trajectories without temporal data leakage.*  
  > *To solve this, we implemented a layered distributed architecture spanning Hadoop HDFS, custom Java Pig UDFs, Apache Hive, PySpark NLP, and Spark MLlib."*

---

### [1:00 – 2:30] Phase 1 & 2: Ingestion and Distributed ETL (Pig + Java UDFs)
- **Screen Action**: Open the terminal. Run or show:
  ```bash
  hdfs dfs -ls -h /yelp_project/raw/
  cat udf/YelpReviewParser.java | head -n 35
  ```
- **Spoken Script**:
  > *"Starting with ingestion, the raw business and review datasets are stored in HDFS at `/yelp_project/raw/` across 128 MB blocks.*  
  > *Because customer reviews contain unescaped line breaks, quotes, and tab characters, standard JSON loaders break record boundaries in downstream tools.*  
  > *To solve this, we authored two custom Java evaluation functions extending Pig's `EvalFunc<Tuple>`: `YelpBusinessParser` and `YelpReviewParser`.*  
  > *As seen here in `YelpReviewParser.java`, we sanitize all newline and tab characters into single spaces, enforce strict schema typing, and output clean tab-delimited tuples into `/yelp_project/processed/` using Pig Latin scripts."*

---

### [2:30 – 4:00] Phase 3: Relational Warehousing & OLAP (Hive)
- **Screen Action**: Show `hive/create_tables.sql` and display exported results in `results/exported/hive/`.
- **Spoken Script**:
  > *"Next, in Phase 3, we built an OLAP data warehouse in Apache Hive under database `yelp_project`.*  
  > *Using schema-on-read external tables pointing to our processed HDFS partitions, we ran relational analytics exploring regional patterns, category dominance, and popularity-quality divergence.*  
  > *Key findings revealed:*  
  > *1. A heavily positive bimodal rating distribution where 4.0 and 4.5 stars make up nearly 39% of all businesses.*  
  > *2. Geographic dominance by Pennsylvania (34,000+ businesses, 1.59M reviews) and Florida (26,000+ businesses, 1.16M reviews).*  
  > *3. Major regional rating disparities: California leads with an average of 4.00 stars, while Delaware trails at 3.35 stars.*  
  > *4. By joining reviews with businesses and analyzing high-volume establishments, we discovered prominent venues with over 5,000 reviews averaging only 3.4 stars, proving that engagement volume does not guarantee customer satisfaction."*

---

### [4:00 – 5:30] Phase 4: Scalable NLP & Aspect Sentiment Mining (PySpark)
- **Screen Action**: Show `spark/business_quality_analysis.py` and open `visualizations/06_aspect_mentions_breakdown.png` and `visualizations/10_top_customer_terms.png`.
- **Spoken Script**:
  > *"Star ratings only tell us how a business is rated, but not why.*  
  > *In Phase 4, we implemented a distributed PySpark NLP pipeline. We tokenized nearly 7 million reviews, stripped English stopwords, and used CountVectorizer to identify dominant operational tokens.*  
  > *We then extracted 8 key operational dimensions: Food Taste, Service, Price, Hospitality, Ambience, Cleanliness, Waiting Time, and Location.*  
  > *Across over 14.8 million aspect mentions, Food Taste and Service comprised over 50% of customer discourse.*  
  > *For every single business, our pipeline computed multi-dimensional aspect profiles tracking positive, neutral, and negative sentiment percentages across all 8 criteria."*

---

### [5:30 – 7:15] Phase 5: Out-of-Time Forecasting (Spark MLlib)
- **Screen Action**: Show `spark/business_quality_prediction.py` and highlight the consecutive-year pairing and temporal split logic.
- **Spoken Script**:
  > *"Phase 5 addresses predictive modeling using Spark MLlib.*  
  > *Most academic papers use random cross-validation, which introduces severe temporal data leakage—allowing future reviews from 2021 to leak into predictions for 2018.*  
  > *We eliminated this lookahead bias by formulating an out-of-time consecutive-year prediction task.*  
  > *Reviews are grouped by calendar year. For every business, we compute operational features in year $t$—including average rating, log review count, review length, rating standard deviation, and sentiment distributions.*  
  > *The target label is the future rating change in year $t+1$, classified into Improving ($\ge +0.25$), Declining ($\le -0.25$), or Stable.*  
  > *We strictly partition our data: earlier transitions are used for training, and recent transitions are held out as an unseen test cohort of 21,224 business-year instances.*  
  > *Using a distributed Random Forest classifier with 60 trees, we trained the model across the cluster."*

---

### [7:15 – 8:45] Phase 6: Empirical Results & Visual Analytics
- **Screen Action**: Display `visualizations/08_model_performance_metrics.png` and `visualizations/07_confusion_matrix_heatmap.png`.
- **Spoken Script**:
  > *"Evaluating our model on the held-out test set yielded strong empirical results:*  
  > *Our Random Forest achieved 46.83% accuracy and an F1-score of 0.4660.*  
  > *Comparing against baselines: random guessing yields 33.33%, while a naive majority class baseline achieves 38.12% accuracy but suffers an F1 collapse to 0.2103 because it predicts zero Improving or Stable cases.*  
  > *Our model achieves a +22.8% relative accuracy gain and a +121.6% relative F1 gain over the majority baseline.*  
  > *Looking at our confusion matrix heatmap, notice our highest recall is on the Improving class at 57.24%, proving that businesses on a recovery trajectory exhibit strong, detectable leading indicators."*

---

### [8:45 – 9:30] Limitations & Architectural Tradeoffs
- **Screen Action**: Scroll through `docs/FINAL_REPORT.md` (Sections 9 and 10).
- **Spoken Script**:
  > *"We also evaluated key engineering tradeoffs and limitations:*  
  > *First, pre-cleaning with Pig and Java UDFs proved superior to Spark's native JSON loader, which choked on corrupt multiline delimiters.*  
  > *Second, we recognize dataset limitations: survivorship bias naturally truncates closed establishments, and regex-based aspect mining lacks the nuanced sarcasm detection of transformer models.*  
  > *For future extensions, we propose integrating Apache Kafka and Flink for sub-second streaming ingestion and deploying DistilBERT embeddings on GPU worker nodes."*

---

### [9:30 – 10:00] Conclusion & Submission Checklist
- **Screen Action**: Show repository root directory with all verified folders (`results/`, `visualizations/`, `docs/`, `pig/`, `hive/`, `spark/`).
- **Spoken Script**:
  > *"In conclusion, this project delivers a production-grade, reproducible big data platform spanning storage, ETL, data warehousing, distributed NLP, and leakage-free predictive modeling.*  
  > *All code, compiled JARs, SQL queries, Spark scripts, 11 publication-grade figures, and our 10-page final report are verified and available in the repository.*  
  > *Thank you!"*
