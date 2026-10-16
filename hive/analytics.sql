USE yelp_project;

-- ============================================================
-- 1. BUSINESS COUNT BY STATE
-- ============================================================

INSERT OVERWRITE DIRECTORY '/yelp_project/results/businesses_by_state'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT
    state,
    COUNT(*) AS business_count
FROM business
WHERE state IS NOT NULL
GROUP BY state
ORDER BY business_count DESC;


-- ============================================================
-- 2. AVERAGE BUSINESS RATING BY STATE
-- ============================================================

INSERT OVERWRITE DIRECTORY '/yelp_project/results/avg_rating_by_state'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT
    state,
    ROUND(AVG(stars), 2) AS avg_rating,
    COUNT(*) AS business_count
FROM business
WHERE state IS NOT NULL
GROUP BY state
HAVING COUNT(*) >= 100
ORDER BY avg_rating DESC;


-- ============================================================
-- 3. TOP 20 MOST REVIEWED BUSINESSES
-- ============================================================

INSERT OVERWRITE DIRECTORY '/yelp_project/results/top_reviewed_businesses'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT
    business_id,
    name,
    city,
    state,
    stars,
    review_count
FROM business
WHERE business_id IS NOT NULL
ORDER BY review_count DESC
LIMIT 20;


-- ============================================================
-- 4. BUSINESS RATING DISTRIBUTION
-- ============================================================

INSERT OVERWRITE DIRECTORY '/yelp_project/results/rating_distribution'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT
    stars,
    COUNT(*) AS business_count
FROM business
WHERE stars IS NOT NULL
GROUP BY stars
ORDER BY stars;


-- ============================================================
-- 5. TOP 20 BUSINESS CATEGORIES
-- ============================================================

INSERT OVERWRITE DIRECTORY '/yelp_project/results/top_categories'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT
    TRIM(category) AS category,
    COUNT(*) AS business_count
FROM business
LATERAL VIEW explode(split(categories, ',')) c AS category
WHERE categories IS NOT NULL
  AND TRIM(category) <> ''
GROUP BY TRIM(category)
ORDER BY business_count DESC
LIMIT 20;


-- ============================================================
-- 6. REVIEW ANALYSIS BY STATE
-- ============================================================

INSERT OVERWRITE DIRECTORY '/yelp_project/results/reviews_by_state'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT
    b.state,
    COUNT(r.review_id) AS review_count,
    ROUND(AVG(r.stars), 2) AS avg_review_rating
FROM business b
JOIN review r
    ON b.business_id = r.business_id
WHERE b.state IS NOT NULL
GROUP BY b.state
ORDER BY review_count DESC;


-- ============================================================
-- 7. POPULARITY VS QUALITY
-- ============================================================

INSERT OVERWRITE DIRECTORY '/yelp_project/results/popularity_vs_quality'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT
    b.business_id,
    b.name,
    b.city,
    b.state,
    b.stars AS business_rating,
    b.review_count,
    COUNT(r.review_id) AS actual_review_count,
    ROUND(AVG(r.stars), 2) AS avg_review_rating
FROM business b
JOIN review r
    ON b.business_id = r.business_id
GROUP BY
    b.business_id,
    b.name,
    b.city,
    b.state,
    b.stars,
    b.review_count
HAVING COUNT(r.review_id) >= 100
ORDER BY actual_review_count DESC
LIMIT 20;
