# Yelp Big Data Analytics & Temporal Business Quality Forecasting Pipeline

An end-to-end distributed Big Data engineering and machine learning platform built on **Hadoop (HDFS)**, **Apache Pig**, **Java UDFs**, **Apache Hive**, and **Apache Spark (PySpark & Spark MLlib)**. The system ingests, cleans, warehouses, analyzes, and models the Yelp Open Academic Dataset (5.1+ GB, 150,346 businesses, and nearly 7 million customer reviews) to uncover regional market patterns, customer sentiment dimensions, and predict future business trajectory without data leakage.

---

## Table of Contents
1. [Executive Summary & Problem Statement](#executive-summary--problem-statement)
2. [Architecture & System Flow](#architecture--system-flow)
3. [Technology Stack](#technology-stack)
4. [Repository Directory Structure](#repository-directory-structure)
5. [Pipeline Stages & Implementation Details](#pipeline-stages--implementation-details)
   - [Phase 1: Ingestion & Distributed Storage (HDFS)](#phase-1-ingestion--distributed-storage-hdfs)
   - [Phase 2: Custom Java UDFs & Pig Latin ETL](#phase-2-custom-java-udfs--pig-latin-etl)
   - [Phase 3: Relational Data Warehousing & OLAP (Hive)](#phase-3-relational-data-warehousing--olap-hive)
   - [Phase 4: Scalable NLP & Aspect-Based Sentiment (PySpark)](#phase-4-scalable-nlp--aspect-based-sentiment-pyspark)
   - [Phase 5: Out-of-Time Temporal Quality Forecasting (Spark MLlib)](#phase-5-out-of-time-temporal-quality-forecasting-spark-mllib)
   - [Phase 6: Automated Visualization Suite](#phase-6-automated-visualization-suite)
6. [Step-by-Step Reproduction Guide](#step-by-step-reproduction-guide)
7. [Key Analytical Findings & Model Evaluation](#key-analytical-findings--model-evaluation)
8. [Generated Visual Assets](#generated-visual-assets)

---

## Executive Summary & Problem Statement

Modern online review platforms like Yelp generate massive streams of semi-structured text and relational metadata. However, extracting actionable intelligence from multi-gigabyte datasets presents major big data challenges:
- **Scalability & Data Cleaning**: Raw JSON contains escaped characters, multiline text, tabs, and unescaped delimiters that break standard batch processing tools.
- **Dimensional Quality Gaps**: High review counts do not necessarily correlate with service quality; businesses with thousands of reviews often show declining satisfaction.
- **Predictive Data Leakage**: Standard machine learning workflows frequently use random cross-validation on time-series records, allowing future customer reviews to leak into past feature representations.

This project addresses these challenges with a production-grade lambda-style batch pipeline:
1. Cleans and normalizes semi-structured JSON records at multi-gigabyte scale using **Apache Pig** and **custom Java UDFs**.
2. Establishes a structured **Hive data warehouse** for aggregate business statistics, state-level performance, category dominance, and popularity-quality divergence.
3. Implements **aspect-based natural language processing (NLP)** in **Spark** across 8 core service dimensions (Food Taste, Service, Price, Hospitality, Ambience, Cleanliness, Waiting Time, Location).
4. Employs a strict **temporal out-of-time train/test split** with **Spark MLlib's Random Forest Classifier** to forecast whether a business will improve, remain stable, or decline in the subsequent operating year.

---

## Architecture & System Flow

```
+----------------------------------------------------------------------------------------------------+
|                                    RAW DATA INGESTION (HDFS)                                       |
|  - yelp_academic_dataset_business.json (113.4 MB, 150,346 businesses)                              |
|  - yelp_academic_dataset_review.json   (5.0 GB, ~6.99M reviews)                                    |
|  Stored in HDFS: /yelp_project/raw/                                                                |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                               ETL PROCESSING & SCHEMA ENFORCEMENT                                  |
|  - Custom Java EvalFunc UDFs: YelpBusinessParser & YelpReviewParser (strip \r, \n, \t delimiters)   |
|  - Apache Pig Latin Scripts: pig/business_etl.pig & pig/review_etl.pig                             |
|  Stored in HDFS: /yelp_project/processed/business & /yelp_project/processed/review                 |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
                         v                                                 v
+--------------------------------------------------+ +-----------------------------------------------+
|         HIVE DATA WAREHOUSE & ANALYTICS          | |       SPARK NLP & BUSINESS PROFILING          |
|  - External Tab-Delimited Tables (yelp_project)  | |  - StopWordsRemover, Tokenizer, CountVector   |
|  - Queries: Rating distribution, State rankings, | |  - Aspect Mining: 8 Dimensions (Food, Service,|
|    Review volume, Top categories, Quality vs Pop | |    Price, Wait, Ambience, Cleanliness, etc.)  |
|  Results: /yelp_project/results/hive/            | |  Results: /yelp_project/results/spark_business|
+--------------------------------------------------+ +-----------------------+-----------------------+
                                                                             |
                                                                             v
+----------------------------------------------------------------------------------------------------+
|                         TEMPORAL PREDICTIVE MODELING (SPARK MLLIB)                                 |
|  - Consecutive-year pairing: Year t (Features) -> Year t+1 (Future Rating Change Target)           |
|  - Strict Temporal Split: Train on earlier years, evaluate on held-out recent years (No Leakage)   |
|  - Random Forest Multiclass Classifier (Declining vs Stable vs Improving)                          |
|  Results: /yelp_project/results/spark_quality_prediction/ (Model, Metrics, Confusion Matrix)       |
+-------------------------------------------------+--------------------------------------------------+
                                                  |
                                                  v
+----------------------------------------------------------------------------------------------------+
|                           VISUAL ANALYTICS & INSIGHTS GENERATION                                   |
|  - Automated Python Suite: visualizations/generate_charts.py (Matplotlib, Seaborn, Pandas)         |
|  - 11 Publication-grade 300-DPI visual figures in visualizations/                                  |
+----------------------------------------------------------------------------------------------------+
```

---

## Technology Stack

| Layer | Component | Version / Specification | Role in System |
|---|---|---|---|
| **OS / Runtime** | Linux Ubuntu on WSL2 | Ubuntu 24.04 LTS (x86_64) | Host environment |
| **Java Platform** | OpenJDK | Java 17 / 8 compatibility | UDF runtime & Hadoop execution |
| **Distributed Storage** | Apache Hadoop HDFS | Hadoop 3.x | Fault-tolerant distributed data storage |
| **ETL & Data Flow** | Apache Pig & Java UDFs | Pig 0.17.0, JSON-Simple 1.1.1 | Robust parsing, cleaning, delimiter sanitation |
| **Data Warehousing** | Apache Hive | Hive 4.0.0 (Derby Metastore) | Schema-on-read, SQL OLAP, state & category rollup |
| **Distributed Compute** | Apache Spark | Spark 4.2.0 (PySpark) | Large-scale NLP tokenization & aspect extraction |
| **Machine Learning** | Spark MLlib | Random Forest, VectorAssembler | Temporal classification without target leakage |
| **Visual Analytics** | Python Data Stack | Python 3.12, Pandas, Matplotlib, Seaborn | 11 publication-grade analytical charts |

---

## Repository Directory Structure

```
yelp-bigdata-project/
├── YelpBusinessParser.jar         # Compiled root Java UDF for Business JSON parsing
├── YelpReviewParser.jar           # Compiled root Java UDF for Review JSON sanitization
├── README.md                      # Comprehensive system documentation
├── data/                          # Local data staging directory
├── docs/                          # In-depth architectural & final project reports
│   └── FINAL_REPORT.md            # Complete 8-10 page academic/industry project report
├── hdfs/                          # HDFS configuration scripts & storage helpers
├── hive/                          # Hive SQL DDL and analytical scripts
│   ├── create_tables.sql          # External table schema definitions in yelp_project
│   └── analytics.sql              # 7 analytical queries with HDFS directory exports
├── logs/                          # Archived execution logs and metastore traces
├── pig/                           # Apache Pig scripts for distributed ETL
│   ├── business_etl.pig           # ETL pipeline for raw business records
│   ├── review_etl.pig             # ETL pipeline for raw review records
│   ├── test_hdfs_read.pig         # Diagnostic script for HDFS read verification
│   └── test_udf_hdfs.pig          # Diagnostic script for UDF schema verification
├── results/                       # Local copies of exported cluster analytics
│   ├── phase1/                    # Raw ingestion logs, disk usage, and record counts
│   └── exported/                  # Exported datasets from Hive and PySpark
│       ├── hive/                  # Hive OLAP exports (state, categories, ratings)
│       ├── spark_business_quality/# Aspect summaries, business profiles, top terms
│       └── spark_quality_prediction/# Confusion matrix, evaluation metrics, predictions
├── screenshots/                   # Verification screenshots of CLI & execution stages
├── spark/                         # PySpark NLP and MLlib machine learning pipelines
│   ├── business_quality_analysis.py # Aspect sentiment mining & business profile agg
│   └── business_quality_prediction.py # Temporal out-of-time Random Forest classifier
├── udf/                           # Java User-Defined Functions source code & unit tests
│   ├── YelpBusinessParser.java    # Pig EvalFunc UDF for business JSON parsing
│   ├── YelpReviewParser.java      # Pig EvalFunc UDF with text whitespace sanitizer
│   ├── test_business.json         # Unit test payload for business parser
│   ├── test_review.json           # Unit test payload for review parser
│   ├── test_udf.pig               # Local Pig verification for business parser
│   └── test_review_udf.pig        # Local Pig verification for review parser
├── venv/                          # Python virtual environment for analytical plotting
└── visualizations/                # Automated plotting script and output charts
    ├── generate_charts.py         # Script generating all 11 analytical figures
    ├── 01_rating_distribution.png # Distribution of business star ratings
    ├── 02_state_business_distribution.png # Businesses by state
    ├── 03_state_avg_rating_comparison.png # State-level average ratings
    ├── 04_state_review_volume_vs_rating.png # Dual-axis state review volume & rating
    ├── 05_top_business_categories.png     # Top 15 business categories
    ├── 06_aspect_mentions_breakdown.png   # 8-dimensional aspect sentiment volume
    ├── 07_confusion_matrix_heatmap.png    # Raw & normalized ML confusion matrix
    ├── 08_model_performance_metrics.png  # Accuracy, Precision, Recall, F1
    ├── 09_class_distribution_actual_vs_predicted.png # Test class distribution
    ├── 10_top_customer_terms.png          # Top 20 customer review tokens
    └── 11_popularity_vs_quality_scatter.png # Review volume vs rating scatter plot
```

---

## Pipeline Stages & Implementation Details

### Phase 1: Ingestion & Distributed Storage (HDFS)
The raw dataset was uploaded to HDFS at `/yelp_project/raw/`:
- `yelp_academic_dataset_business.json`: 113.4 MB (150,346 records)
- `yelp_academic_dataset_review.json`: 5.0 GB (~6,990,280 records)
- Total distributed footprint: 5.1 GB.

Verification command:
```bash
hdfs dfs -ls -h /yelp_project/raw/
hdfs dfs -du -h /yelp_project/raw/
```

### Phase 2: Custom Java UDFs & Pig Latin ETL
Processing raw JSON directly via standard string splitting fails due to arbitrary nested punctuation, line feeds (`\n`, `\r`), and tabs inside customer review texts. Two custom Java UDFs extending `org.apache.pig.EvalFunc<Tuple>` were implemented using `json-simple`:
1. **`YelpBusinessParser.java`**:
   - Parses `business_id`, `name`, `city`, `state`, `stars`, `review_count`, `is_open`, `categories`.
   - Returns typed Pig Tuples with an explicit `@OutputSchema`.
2. **`YelpReviewParser.java`**:
   - Extracts `review_id`, `user_id`, `business_id`, `stars`, `useful`, `funny`, `cool`, `text`, `date`.
   - **Critical Sanitization**: Replaces `\r`, `\n`, and `\t` with single spaces, preventing corruption of tab-delimited records in subsequent MapReduce/Hive stages.

Pig Scripts execute distributed filtering to drop records with null identifiers or null ratings, outputting tab-delimited files to:
- `/yelp_project/processed/business`
- `/yelp_project/processed/review`

### Phase 3: Relational Data Warehousing & OLAP (Hive)
Hive external tables (`business` and `review`) are declared under database `yelp_project` pointing directly to the processed HDFS paths. 

Key analytical queries executed in `hive/analytics.sql`:
1. **Business Count by State**: Aggregates business density (PA leads with 34,039, FL with 26,330).
2. **Average Rating by State**: Filters for regions with $\ge 100$ businesses (California achieves highest average rating at 4.00; Delaware lowest at 3.35).
3. **Rating Distribution**: Groups by discrete star ratings from 1.0 to 5.0 stars (bimodal curve peaking at 4.0 stars).
4. **Top 20 Business Categories**: Uses `LATERAL VIEW explode(split(categories, ','))` to parse comma-separated tags (Restaurants: 52,268; Food: 27,781; Shopping: 24,395).
5. **Review Analysis by State**: Joins business and review tables to aggregate over 6.99M reviews (PA: 1.59M reviews; FL: 1.16M reviews).
6. **Popularity vs. Quality Divergence**: Evaluates whether high review counts guarantee high satisfaction (revealing prominent restaurants like *Mother's Restaurant* with 5,185 reviews averaging 3.44 stars).

### Phase 4: Scalable NLP & Aspect-Based Sentiment (PySpark)
Using PySpark (`spark/business_quality_analysis.py`), review texts undergo tokenization, case normalization, and stopwords removal:
- **Lexical Extraction**: A `CountVectorizer` models top unigrams (identifying high-frequency operational tokens: *food, service, time, staff, friendly, clean, wait, delicious*).
- **Aspect Dimension Mining**: 8 regex dictionaries match reviews mentioning specific operational aspects:
  - `food_taste`: 3,845,236 mentions
  - `service`: 3,541,582 mentions
  - `hospitality`: 1,915,796 mentions
  - `waiting_time`: 1,409,456 mentions
  - `location`: 1,291,929 mentions
  - `price`: 1,279,365 mentions
  - `ambience`: 1,030,048 mentions
  - `cleanliness`: 527,451 mentions
- **Granular Business Quality Profiles**: Each business receives positive, neutral, and negative sentiment percentages across all 8 aspects alongside aggregate rating volume and text lengths, exported to `/yelp_project/results/spark_business_quality/business_profiles`.

### Phase 5: Out-of-Time Temporal Quality Forecasting (Spark MLlib)
Predicting future business trajectories (`spark/business_quality_prediction.py`) requires avoiding random cross-validation, which causes temporal data leakage.
1. **Consecutive-Year Pairing**: Reviews are grouped by `(business_id, review_year)`. Year $t$ is paired with year $t+1$.
2. **Target Labeling**:
   - $\Delta \text{Rating} = \overline{R}_{t+1} - \overline{R}_{t}$
   - **Improving** ($\Delta \ge +0.25$)
   - **Declining** ($\Delta \le -0.25$)
   - **Stable** ($-0.25 < \Delta < +0.25$)
3. **Temporal Partitioning**:
   - Model trains strictly on earlier transitions ($t < \text{cutoff} - 1$).
   - Model tests on the held-out subsequent years ($t \ge \text{cutoff}$).
   - Total test instances: **21,224 business-year pairs**.
4. **Model Architecture**:
   - Features: `current_avg_rating`, `log_review_count`, `avg_review_length`, `positive_pct`, `negative_pct`, `neutral_pct`, `rating_stddev`.
   - Algorithm: `RandomForestClassifier` (`numTrees=60`, `maxDepth=8`, `seed=42`).
   - Results: **46.83% Accuracy**, **0.4660 F1 score**, outperforming the random guess baseline (33.33%) and majority class baseline (38.12%).

### Phase 6: Automated Visualization Suite
The automated plotting script (`visualizations/generate_charts.py`) reads exported datasets from HDFS/local results and produces 11 publication-grade charts formatted with consistent modern styling (300 DPI, tailored palettes, explicit value labels).

---

## Step-by-Step Reproduction Guide

### Prerequisites
Ensure Hadoop, Hive, and Spark are configured in your environment:
```bash
# Verify services
hdfs dfsadmin -report
hive --version
spark-submit --version
```

### 1. Ingest Data into HDFS
```bash
hdfs dfs -mkdir -p /yelp_project/raw
hdfs dfs -put data/yelp_academic_dataset_business.json /yelp_project/raw/
hdfs dfs -put data/yelp_academic_dataset_review.json /yelp_project/raw/
```

### 2. Compile Java UDFs and Run Pig ETL
```bash
# Compile UDFs
cd udf
javac -cp $(pig -secretDumpEnv | grep PIG_CLASSPATH | cut -d= -f2):/usr/share/java/json-simple.jar YelpBusinessParser.java YelpReviewParser.java
jar -cf YelpBusinessParser.jar YelpBusinessParser*.class
jar -cf YelpReviewParser.jar YelpReviewParser*.class
cp Yelp*.jar ../
cd ..

# Execute ETL scripts
pig -x mapreduce pig/business_etl.pig
pig -x mapreduce pig/review_etl.pig
```

### 3. Run Hive Data Warehousing & OLAP Queries
```bash
hive -f hive/create_tables.sql
hive -f hive/analytics.sql

# Export Hive results locally
mkdir -p results/exported/hive
hdfs dfs -get /yelp_project/results/* results/exported/hive/
```

### 4. Execute PySpark NLP & Machine Learning Pipelines
```bash
# Execute Aspect-Based Sentiment Analysis
spark-submit --master local[*] spark/business_quality_analysis.py

# Execute Out-of-Time Predictive Modeling
spark-submit --master local[*] spark/business_quality_prediction.py

# Export Spark results locally
mkdir -p results/exported/spark_business_quality results/exported/spark_quality_prediction
hdfs dfs -get /yelp_project/results/spark_business_quality/* results/exported/spark_business_quality/
hdfs dfs -get /yelp_project/results/spark_quality_prediction/* results/exported/spark_quality_prediction/
```

### 5. Generate Publication Visualizations
```bash
source venv/bin/activate
python visualizations/generate_charts.py
```

---

## Key Analytical Findings & Model Evaluation

### 1. Rating Distribution Characteristics
Analysis of 150,346 businesses indicates that Yelp reviews are overwhelmingly positive, exhibiting a bimodal distribution skewed toward high ratings:
- 4.0 Stars: 31,125 businesses (20.7%)
- 4.5 Stars: 27,181 businesses (18.1%)
- 3.5 Stars: 26,519 businesses (17.6%)
- 1.0 - 2.0 Stars: Only 16,445 businesses combined (10.9%)

### 2. Geographic Polarization
- **Volume Hubs**: Pennsylvania (34,039 businesses, 1.59M reviews) and Florida (26,330 businesses, 1.16M reviews) dominate the geographic distribution.
- **Rating Disparities**: California businesses average 4.00 stars, significantly outperforming New Jersey (3.46 stars), Illinois (3.37 stars), and Delaware (3.35 stars).

### 3. Aspect Focus
Customer discourse is heavily centered on core tangible experiences:
- **Food Taste** (3.85M mentions) and **Service** (3.54M mentions) comprise over 50% of all aspect discussions.
- Cleanliness is mentioned least frequently (527K mentions), but when present in 1-star reviews, negative sentiment regarding hygiene correlates with steep future rating drops.

### 4. Predictive Model Performance Summary

| Metric | Random Guess Baseline | Majority Class Baseline | Spark MLlib Random Forest | Relative Improvement |
|---|---|---|---|---|
| **Accuracy** | 33.33% | 38.12% | **46.83%** | **+22.8% over majority** |
| **Weighted Precision** | 33.33% | 38.12% | **47.33%** | **+24.2% over majority** |
| **Weighted Recall** | 33.33% | 38.12% | **46.83%** | **+22.8% over majority** |
| **F1-Score** | 33.33% | 21.03% | **46.60%** | **+121.6% over majority** |

#### Confusion Matrix (Test Set: N = 21,224)

| Actual \ Predicted | Declining | Stable | Improving | Total Actual | Class Recall |
|---|---|---|---|---|---|
| **Declining** | **3,122** | 2,680 | 2,288 | 8,090 | **38.59%** |
| **Stable** | 2,171 | **3,733** | 1,840 | 7,744 | **48.21%** |
| **Improving** | 1,154 | 1,151 | **3,085** | 5,390 | **57.24%** |
| **Total Predicted** | 6,447 | 7,564 | 7,213 | **21,224** | **Overall: 46.83%** |

---

## Generated Visual Assets

All visual charts are exported to `visualizations/`:
1. `01_rating_distribution.png`: Business star rating frequency and percentage share.
2. `02_state_business_distribution.png`: Business volume across top states.
3. `03_state_avg_rating_comparison.png`: Average rating by state with cross-state mean baseline.
4. `04_state_review_volume_vs_rating.png`: Dual-axis review volume and average star rating.
5. `05_top_business_categories.png`: Top 15 business categories in Yelp.
6. `06_aspect_mentions_breakdown.png`: Mention frequency across 8 operational quality dimensions.
7. `07_confusion_matrix_heatmap.png`: Raw and row-normalized confusion matrix heatmaps.
8. `08_model_performance_metrics.png`: Model accuracy, precision, recall, and F1 vs baselines.
9. `09_class_distribution_actual_vs_predicted.png`: Ground truth vs predicted class balance.
10. `10_top_customer_terms.png`: Top 20 customer review tokens from CountVectorizer.
11. `11_popularity_vs_quality_scatter.png`: Review volume vs rating scatter plot highlighting quality divergence.

---
*For a comprehensive research report including complete statistical analyses, methodological proofs, and architectural tradeoffs, refer to [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md).*