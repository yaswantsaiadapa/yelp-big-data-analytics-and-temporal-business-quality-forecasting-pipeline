import java.io.IOException;

import org.apache.pig.EvalFunc;
import org.apache.pig.builtin.OutputSchema;
import org.apache.pig.data.Tuple;
import org.apache.pig.data.TupleFactory;

import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

@OutputSchema("(review_id:chararray,"
            + "user_id:chararray,"
            + "business_id:chararray,"
            + "stars:double,"
            + "useful:int,"
            + "funny:int,"
            + "cool:int,"
            + "text:chararray,"
            + "date:chararray)")
public class YelpReviewParser extends EvalFunc<Tuple> {

    private static final TupleFactory tupleFactory =
        TupleFactory.getInstance();

    @Override
    public Tuple exec(Tuple input) throws IOException {

        if (input == null || input.size() == 0 || input.get(0) == null) {
            return null;
        }

        try {
            String json = input.get(0).toString();

            JSONParser parser = new JSONParser();
            JSONObject obj = (JSONObject) parser.parse(json);

            Tuple output = tupleFactory.newTuple(9);

            output.set(0, obj.get("review_id"));
            output.set(1, obj.get("user_id"));
            output.set(2, obj.get("business_id"));
            output.set(3, obj.get("stars"));
            output.set(4, obj.get("useful"));
            output.set(5, obj.get("funny"));
            output.set(6, obj.get("cool"));

	    String text = obj.get("text") == null
	        ? null
        	: obj.get("text").toString()
            	.replace("\r", " ")
            	.replace("\n", " ")
            	.replace("\t", " ");

output.set(7, text);


            output.set(8, obj.get("date"));

            return output;

        } catch (Exception e) {
            throw new IOException(
                "JSON parsing failed: " + e.getMessage(), e
            );
        }
    }
}
