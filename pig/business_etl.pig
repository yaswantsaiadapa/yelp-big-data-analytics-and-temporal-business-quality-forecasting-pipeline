REGISTER '/home/yaswantsaiadapa/yelp-bigdata-project/YelpBusinessParser.jar';

business_lines = LOAD '/yelp_project/raw/yelp_academic_dataset_business.json'
    USING TextLoader();

business_raw = FOREACH business_lines GENERATE
    YelpBusinessParser($0) AS parsed;

business_flat = FOREACH business_raw GENERATE
    parsed.business_id AS business_id,
    parsed.name AS name,
    parsed.city AS city,
    parsed.state AS state,
    parsed.stars AS stars,
    parsed.review_count AS review_count,
    parsed.is_open AS is_open,
    parsed.categories AS categories;

business_clean = FILTER business_flat BY
    business_id IS NOT NULL
    AND stars IS NOT NULL
    AND review_count IS NOT NULL;

STORE business_clean
    INTO '/yelp_project/processed/business'
    USING PigStorage('\t');
