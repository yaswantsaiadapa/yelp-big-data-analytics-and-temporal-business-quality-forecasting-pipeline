REGISTER 'YelpBusinessParser.jar';

raw = LOAD 'test_business.json'
      USING TextLoader();

parsed = FOREACH raw GENERATE
         YelpBusinessParser($0);

DUMP parsed;
