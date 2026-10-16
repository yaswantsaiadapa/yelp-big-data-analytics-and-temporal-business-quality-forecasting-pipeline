CREATE DATABASE IF NOT EXISTS yelp_project;

USE yelp_project;

DROP TABLE IF EXISTS business;

CREATE EXTERNAL TABLE business (
    business_id STRING,
    name STRING,
    city STRING,
    state STRING,
    stars DOUBLE,
    review_count INT,
    is_open INT,
    categories STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/yelp_project/processed/business';


DROP TABLE IF EXISTS review;

CREATE EXTERNAL TABLE review (
    review_id STRING,
    user_id STRING,
    business_id STRING,
    stars DOUBLE,
    useful INT,
    funny INT,
    cool INT,
    text STRING,
    review_date STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/yelp_project/processed/review';