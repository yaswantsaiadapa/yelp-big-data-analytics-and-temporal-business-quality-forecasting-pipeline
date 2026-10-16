REGISTER 'YelpReviewParser.jar';

raw = LOAD 'test_review.json'
      USING TextLoader();

parsed = FOREACH raw GENERATE
         YelpReviewParser($0);

DUMP parsed;
