REGISTER '/home/yaswantsaiadapa/yelp-bigdata-project/YelpBusinessParser.jar';

raw = LOAD '/yelp_project/raw/yelp_academic_dataset_business.json'
      USING TextLoader();

parsed = FOREACH raw GENERATE YelpBusinessParser($0);

DUMP parsed;
