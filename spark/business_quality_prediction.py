
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, avg, length, year, to_date, when, lit,
    stddev, log, coalesce, max as spark_max, abs as spark_abs
)
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# --------------------------------------------------
# 1. SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("YelpTemporalBusinessQualityPrediction")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# --------------------------------------------------
# 2. INPUT AND OUTPUT PATHS
# --------------------------------------------------

review_path = "/yelp_project/processed/review"

output_base = "/yelp_project/results/spark_quality_prediction"
predictions_path = output_base + "/predictions"
metrics_path = output_base + "/metrics"
confusion_path = output_base + "/confusion_matrix"
model_path = output_base + "/model"

# --------------------------------------------------
# 3. READ PROCESSED REVIEWS
# --------------------------------------------------

review_schema = """
review_id STRING,
user_id STRING,
business_id STRING,
stars DOUBLE,
useful INT,
funny INT,
cool INT,
text STRING,
date STRING
"""

reviews = (
    spark.read
    .option("sep", "\t")
    .option("header", "false")
    .schema(review_schema)
    .csv(review_path)
)

print("\n========== INPUT DATA ==========")
print("Review records:", reviews.count())

# --------------------------------------------------
# 4. PREPARE YEARLY REVIEW FEATURES
# --------------------------------------------------

reviews = (
    reviews
    .withColumn("review_date", to_date(col("date")))
    .withColumn("review_year", year(col("review_date")))
    .withColumn(
        "review_length",
        length(coalesce(col("text"), lit("")))
    )
    .filter(
        col("business_id").isNotNull()
        & col("stars").between(1.0, 5.0)
        & col("review_year").isNotNull()
    )
)

yearly = (
    reviews
    .groupBy("business_id", "review_year")
    .agg(
        count("*").alias("year_review_count"),
        avg("stars").alias("avg_rating"),
        avg("review_length").alias("avg_review_length"),
        avg(
            when(col("stars") >= 4.0, 1.0).otherwise(0.0)
        ).alias("positive_pct"),
        avg(
            when(col("stars") <= 2.0, 1.0).otherwise(0.0)
        ).alias("negative_pct"),
        avg(
            when(col("stars") == 3.0, 1.0).otherwise(0.0)
        ).alias("neutral_pct"),
        coalesce(stddev("stars"), lit(0.0)).alias("rating_stddev")
    )
)

print("\n========== YEARLY DATA ==========")
yearly.select(
    "business_id", "review_year", "year_review_count", "avg_rating"
).show(10, truncate=False)

# --------------------------------------------------
# 5. PAIR YEAR t WITH YEAR t+1
# --------------------------------------------------
# Features come ONLY from year t.
# The rating from year t+1 is used ONLY to create the target.

current = yearly.alias("current")
future = yearly.alias("future")

pairs = (
    current.join(
        future,
        (
            col("current.business_id") == col("future.business_id")
        ) & (
            col("future.review_year") == col("current.review_year") + 1
        ),
        "inner"
    )
    .select(
        col("current.business_id").alias("business_id"),
        col("current.review_year").alias("year"),
        col("current.year_review_count").alias("review_count"),
        col("current.avg_rating").alias("current_avg_rating"),
        col("current.avg_review_length").alias("avg_review_length"),
        col("current.positive_pct").alias("positive_pct"),
        col("current.negative_pct").alias("negative_pct"),
        col("current.neutral_pct").alias("neutral_pct"),
        col("current.rating_stddev").alias("rating_stddev"),
        col("future.avg_rating").alias("future_avg_rating"),
        col("future.year_review_count").alias("future_review_count")
    )
    .filter(
        (col("review_count") >= 5)
        & (col("future_review_count") >= 5)
    )
    .withColumn(
        "rating_change",
        col("future_avg_rating") - col("current_avg_rating")
    )
    .withColumn(
        "label",
        when(col("rating_change") >= 0.25, 2.0)
        .when(col("rating_change") <= -0.25, 0.0)
        .otherwise(1.0)
    )
    .withColumn(
        "actual_label",
        when(col("label") == 0.0, "Declining")
        .when(col("label") == 1.0, "Stable")
        .otherwise("Improving")
    )
    .withColumn(
        "log_review_count",
        log(col("review_count").cast("double") + lit(1.0))
    )
    .cache()
)

pair_count = pairs.count()

print("\n========== PREDICTION DATA ==========")
print("Eligible business-year pairs:", pair_count)

if pair_count == 0:
    raise RuntimeError(
        "No eligible consecutive-year pairs found. "
        "Check review dates and yearly review counts."
    )

pairs.groupBy("actual_label").count().show()

# --------------------------------------------------
# 6. TEMPORAL TRAIN/TEST SPLIT
# --------------------------------------------------
# The latest two available transition years are held out
# where the data permits. No random split is used.

latest_pair_year = pairs.agg(
    spark_max("year")
).first()[0]

test_cutoff = latest_pair_year - 1

# Exclude the transition immediately before the test period
# to prevent overlap between training outcome years and test features.
train = pairs.filter(col("year") < (test_cutoff - 1))
test = pairs.filter(col("year") >= test_cutoff)



train_count = train.count()
test_count = test.count()

print("\n========== TEMPORAL SPLIT ==========")
print("Latest feature year:", latest_pair_year)
print("Test starts at year:", test_cutoff)
print("Training pairs:", train_count)
print("Testing pairs:", test_count)

train.groupBy("actual_label").count().show()
test.groupBy("actual_label").count().show()

if train_count == 0 or test_count == 0:
    raise RuntimeError(
        "Temporal train/test split is empty. "
        "Inspect available years before training."
    )

# --------------------------------------------------
# 7. BUILD RANDOM FOREST PIPELINE
# --------------------------------------------------

feature_columns = [
    "current_avg_rating",
    "log_review_count",
    "avg_review_length",
    "positive_pct",
    "negative_pct",
    "neutral_pct",
    "rating_stddev"
]

assembler = VectorAssembler(
    inputCols=feature_columns,
    outputCol="features",
    handleInvalid="skip"
)

classifier = RandomForestClassifier(
    labelCol="label",
    featuresCol="features",
    predictionCol="prediction",
    numTrees=60,
    maxDepth=8,
    seed=42
)

pipeline = Pipeline(stages=[assembler, classifier])

# --------------------------------------------------
# 8. TRAIN ON EARLIER YEARS ONLY
# --------------------------------------------------

print("\nTraining Random Forest...")
model = pipeline.fit(train)

print("Training completed.")

# --------------------------------------------------
# 9. PREDICT LATER YEARS
# --------------------------------------------------

predictions = model.transform(test)

predictions = (
    predictions
    .withColumn(
        "predicted_label",
        when(col("prediction") == 0.0, "Declining")
        .when(col("prediction") == 1.0, "Stable")
        .otherwise("Improving")
    )
    .select(
        "business_id",
        "year",
        "review_count",
        "current_avg_rating",
        "future_avg_rating",
        "rating_change",
        "actual_label",
        "predicted_label",
        "label",
        "prediction"
    )
    .cache()
)

print("\n========== SAMPLE PREDICTIONS ==========")
predictions.show(20, truncate=False)

# --------------------------------------------------
# 10. EVALUATE MODEL
# --------------------------------------------------

metric_rows = []

for metric_name in [
    "accuracy",
    "weightedPrecision",
    "weightedRecall",
    "f1"
]:
    evaluator = MulticlassClassificationEvaluator(
        labelCol="label",
        predictionCol="prediction",
        metricName=metric_name
    )

    metric_value = evaluator.evaluate(predictions)

    metric_rows.append((metric_name, float(metric_value)))

print("\n========== TEST METRICS ==========")

for name, value in metric_rows:
    print(f"{name}: {value:.4f}")

print("\n========== CONFUSION MATRIX ==========")

confusion = (
    predictions
    .groupBy("actual_label", "predicted_label")
    .count()
    .orderBy("actual_label", "predicted_label")
)

confusion.show(truncate=False)

# --------------------------------------------------
# 11. SAVE RESULTS AND MODEL TO HDFS
# --------------------------------------------------

(
    predictions.coalesce(1)
    .write.mode("overwrite")
    .option("header", "true")
    .csv(predictions_path)
)

metrics_df = spark.createDataFrame(
    metric_rows,
    ["metric", "value"]
)

(
    metrics_df.coalesce(1)
    .write.mode("overwrite")
    .option("header", "true")
    .csv(metrics_path)
)

(
    confusion.coalesce(1)
    .write.mode("overwrite")
    .option("header", "true")
    .csv(confusion_path)
)

model.write().overwrite().save(model_path)

print("\n========== SAVED OUTPUTS ==========")
print("Predictions:", predictions_path)
print("Metrics:", metrics_path)
print("Confusion matrix:", confusion_path)
print("Trained model:", model_path)

predictions.unpersist()
pairs.unpersist()
spark.stop()

print("\nTemporal quality prediction completed.")
