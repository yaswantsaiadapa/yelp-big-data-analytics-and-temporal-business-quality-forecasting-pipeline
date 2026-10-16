REGISTER '/home/yaswantsaiadapa/yelp-bigdata-project/YelpReviewParser.jar';

review_lines = LOAD '/yelp_project/raw/yelp_academic_dataset_review.json'
    USING TextLoader();

review_raw = FOREACH review_lines GENERATE
    YelpReviewParser($0) AS parsed;

review_flat = FOREACH review_raw GENERATE
    parsed.review_id AS review_id,
    parsed.user_id AS user_id,
    parsed.business_id AS business_id,
    parsed.stars AS stars,
    parsed.useful AS useful,
    parsed.funny AS funny,
    parsed.cool AS cool,
    parsed.text AS text,
    parsed.date AS date;

review_clean = FILTER review_flat BY
    review_id IS NOT NULL
    AND user_id IS NOT NULL
    AND business_id IS NOT NULL
    AND stars IS NOT NULL
    AND text IS NOT NULL
    AND date IS NOT NULL;

STORE review_clean
    INTO '/yelp_project/processed/review'
    USING PigStorage('\t');
