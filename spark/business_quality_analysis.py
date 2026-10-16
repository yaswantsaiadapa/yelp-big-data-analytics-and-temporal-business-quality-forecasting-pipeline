from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    IntegerType
)
from pyspark.sql.functions import (
    col,
    trim,
    lower,
    regexp_replace,
    length,
    split,
    size,
    avg,
    count,
    sum,
    when,
    round,
    explode
)
from pyspark.ml.feature import RegexTokenizer, StopWordsRemover, CountVectorizer


# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = SparkSession.builder \
    .appName("YelpBusinessQualityAnalysis") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


# --------------------------------------------------
# 2. DEFINE SCHEMAS
# --------------------------------------------------

review_schema = StructType([
    StructField("review_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("business_id", StringType(), True),
    StructField("stars", DoubleType(), True),
    StructField("useful", IntegerType(), True),
    StructField("funny", IntegerType(), True),
    StructField("cool", IntegerType(), True),
    StructField("text", StringType(), True),
    StructField("date", StringType(), True)
])

business_schema = StructType([
    StructField("business_id", StringType(), True),
    StructField("name", StringType(), True),
    StructField("city", StringType(), True),
    StructField("state", StringType(), True),
    StructField("stars", DoubleType(), True),
    StructField("review_count", IntegerType(), True),
    StructField("is_open", IntegerType(), True),
    StructField("categories", StringType(), True)
])


# --------------------------------------------------
# 3. READ PROCESSED DATA FROM HDFS
# --------------------------------------------------

reviews = spark.read \
    .schema(review_schema) \
    .option("delimiter", "\t") \
    .csv("/yelp_project/processed/review")

businesses = spark.read \
    .schema(business_schema) \
    .option("delimiter", "\t") \
    .csv("/yelp_project/processed/business")


# --------------------------------------------------
# 4. BASIC DATA CHECK
# --------------------------------------------------

print("========================================")
print("DATASET INFORMATION")
print("========================================")

print("Number of reviews:", reviews.count())
print("Number of businesses:", businesses.count())

print("\nReview schema:")
reviews.printSchema()

print("\nBusiness schema:")
businesses.printSchema()


# --------------------------------------------------
# 5. CALCULATE REVIEW LENGTH
# --------------------------------------------------

reviews = reviews.withColumn(
    "review_length",
    when(
        length(trim(col("text"))) > 0,
        size(split(trim(col("text")), r"\s+"))
    ).otherwise(0)
)

# --------------------------------------------------
# 6. CLEAN REVIEW TEXT
# --------------------------------------------------

reviews = reviews.withColumn(
    "clean_text",
    lower(
        regexp_replace(
            col("text"),
            r"[^a-zA-Z\s]",
            " "
        )
    )
)

reviews = reviews.withColumn(
    "clean_text",
    regexp_replace(
        col("clean_text"),
        r"\s+",
        " "
    )
)


# --------------------------------------------------
# 7. TOKENIZE REVIEW TEXT
# --------------------------------------------------

tokenizer = RegexTokenizer(
    inputCol="clean_text",
    outputCol="words",
    pattern=r"\W+"
)

reviews = tokenizer.transform(reviews)


# --------------------------------------------------
# 8. REMOVE COMMON STOP WORDS
# --------------------------------------------------

remover = StopWordsRemover(
    inputCol="words",
    outputCol="filtered_words"
)

reviews = remover.transform(reviews)


# --------------------------------------------------
# 9. FIND IMPORTANT/FREQUENT TERMS
# --------------------------------------------------

vectorizer = CountVectorizer(
    inputCol="filtered_words",
    outputCol="term_frequency",
    vocabSize=5000,
    minDF=100
)

vectorizer_model = vectorizer.fit(
    reviews.select("filtered_words")
)

vocabulary = vectorizer_model.vocabulary

top_terms = []

for i, word in enumerate(vocabulary[:50]):
    top_terms.append((i + 1, word))

top_terms_df = spark.createDataFrame(
    top_terms,
    ["rank", "term"]
)

print("\n========================================")
print("TOP CUSTOMER-MENTIONED TERMS")
print("========================================")

top_terms_df.show(50, truncate=False)

# --------------------------------------------------
# 10. DEFINE BUSINESS QUALITY ASPECTS
# --------------------------------------------------

aspect_patterns = {
    "food_taste": r"\b(food|taste|tasty|delicious|flavor|flavour|fresh|bland|spicy|salty|sweet|meal|dish|menu)\b",

    "service": r"\b(service|waiter|waitress|server|staff|helpful|rude|friendly|attentive|professional)\b",

    "price": r"\b(price|expensive|cheap|affordable|cost|overpriced|value|worth|pricey)\b",

    "hospitality": r"\b(hospitality|welcome|welcoming|friendly|rude|professional|accommodating|staff)\b",

    "ambience": r"\b(ambience|ambiance|atmosphere|noisy|quiet|comfortable|music|decor|environment)\b",

    "cleanliness": r"\b(clean|dirty|cleanliness|hygiene|sanitary|messy|spotless)\b",

    "waiting_time": r"\b(wait|waiting|queue|delay|slow|quick|minutes)\b",

    "location": r"\b(location|parking|downtown|nearby|area|neighborhood|convenient)\b"
}


# --------------------------------------------------
# 11. DETECT ASPECT MENTIONS
# --------------------------------------------------

for aspect, pattern in aspect_patterns.items():

    reviews = reviews.withColumn(
        aspect + "_mentioned",
        col("clean_text").rlike(pattern).cast("int")
    )


# --------------------------------------------------
# 12. BUSINESS-LEVEL REVIEW STATISTICS
# --------------------------------------------------

business_quality = reviews.groupBy("business_id").agg(
    count("*").alias("total_reviews"),

    round(avg("stars"), 2).alias("average_review_rating"),

    round(avg("review_length"), 2).alias("average_review_length"),

    sum(when(col("stars") <= 2, 1).otherwise(0))
        .alias("negative_reviews"),

    sum(when(col("stars") == 3, 1).otherwise(0))
        .alias("neutral_reviews"),

    sum(when(col("stars") >= 4, 1).otherwise(0))
        .alias("positive_reviews")
)


# --------------------------------------------------
# 13. CALCULATE REVIEW PERCENTAGES
# --------------------------------------------------

business_quality = business_quality.withColumn(
    "negative_review_pct",
    round(
        col("negative_reviews") / col("total_reviews") * 100,
        2
    )
)

business_quality = business_quality.withColumn(
    "neutral_review_pct",
    round(
        col("neutral_reviews") / col("total_reviews") * 100,
        2
    )
)

business_quality = business_quality.withColumn(
    "positive_review_pct",
    round(
        col("positive_reviews") / col("total_reviews") * 100,
        2
    )
)



# --------------------------------------------------
# 14. ASPECT-LEVEL ANALYSIS
# --------------------------------------------------

aspect_aggregations = []

for aspect in aspect_patterns.keys():

    mentioned_col = col(aspect + "_mentioned")

    # Total number of reviews mentioning this aspect
    aspect_aggregations.append(
        sum(mentioned_col).alias(aspect + "_mentions")
    )

    # Positive aspect mentions
    aspect_aggregations.append(
        sum(
            when(
                (mentioned_col == 1) & (col("stars") >= 4),
                1
            ).otherwise(0)
        ).alias(aspect + "_positive")
    )

    # Neutral aspect mentions
    aspect_aggregations.append(
        sum(
            when(
                (mentioned_col == 1) & (col("stars") == 3),
                1
            ).otherwise(0)
        ).alias(aspect + "_neutral")
    )

    # Negative aspect mentions
    aspect_aggregations.append(
        sum(
            when(
                (mentioned_col == 1) & (col("stars") <= 2),
                1
            ).otherwise(0)
        ).alias(aspect + "_negative")
    )



# --------------------------------------------------
# 15. COMBINE BUSINESS STATISTICS + ASPECT ANALYSIS
# --------------------------------------------------
aspect_quality = reviews.groupBy("business_id").agg(
    *aspect_aggregations
)


business_quality = business_quality.join(
    aspect_quality,
    on="business_id",
    how="left"
)

# --------------------------------------------------
# 16. CALCULATE ASPECT POSITIVE/NEGATIVE PERCENTAGES
# --------------------------------------------------

for aspect in aspect_patterns.keys():

    mentions = col(aspect + "_mentions")

    business_quality = business_quality.withColumn(
        aspect + "_positive_pct",
        round(
            when(
                mentions > 0,
                col(aspect + "_positive") / mentions * 100
            ).otherwise(0),
            2
        )
    )

    business_quality = business_quality.withColumn(
        aspect + "_negative_pct",
        round(
            when(
                mentions > 0,
                col(aspect + "_negative") / mentions * 100
            ).otherwise(0),
            2
        )
    )

# --------------------------------------------------
# 17. JOIN BUSINESS INFORMATION
# --------------------------------------------------

business_info = businesses.select(
    "business_id",
    "name",
    "city",
    "state",
    col("stars").alias("business_stars"),
    "review_count",
    "is_open",
    "categories"
)

final_business_quality = business_info.join(
    business_quality,
    on="business_id",
    how="inner"
)

# --------------------------------------------------
# 18. DISPLAY SAMPLE RESULTS
# --------------------------------------------------

print("\n========================================")
print("BUSINESS QUALITY RESULTS")
print("========================================")

final_business_quality.select(
    "business_id",
    "name",
    "city",
    "state",
    "business_stars",
    "total_reviews",
    "average_review_rating",
    "average_review_length",
    "positive_review_pct",
    "negative_review_pct"
).show(20, truncate=False)


# --------------------------------------------------
# 19. SAVE BUSINESS QUALITY RESULTS
# --------------------------------------------------

output_path = "/yelp_project/results/spark_business_quality/business_profiles"

final_business_quality.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(output_path)

print("\nBusiness quality analysis saved to:")
print(output_path)


# --------------------------------------------------
# 20. SAVE IMPORTANT TERMS 
# --------------------------------------------------

terms_output_path = "/yelp_project/results/spark_business_quality/important_terms"

top_terms_df.write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(terms_output_path)

print("\nImportant terms saved to:")
print(terms_output_path)

# --------------------------------------------------
# 21. OVERALL ASPECT SUMMARY
# --------------------------------------------------

print("\n========================================")
print("OVERALL ASPECT SUMMARY")
print("========================================")

# Calculate all aspect totals in one aggregation
aspect_total_expressions = [
    sum(col(f"{aspect}_mentions")).alias(aspect)
    for aspect in aspect_patterns.keys()
]

aspect_totals = final_business_quality.agg(
    *aspect_total_expressions
).first()

overall_aspect_rows = [
    (aspect, aspect_totals[aspect] or 0)
    for aspect in aspect_patterns.keys()
]

overall_aspect_df = spark.createDataFrame(
    overall_aspect_rows,
    ["aspect", "total_mentions"]
)

overall_aspect_df.show(truncate=False)

aspect_output_path = (
    "/yelp_project/results/spark_business_quality/aspect_summary"
)

overall_aspect_df.coalesce(1).write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv(aspect_output_path)

print("\nOverall aspect summary saved to:")
print(aspect_output_path)


# --------------------------------------------------
# 22. STOP SPARK
# --------------------------------------------------

spark.stop()
