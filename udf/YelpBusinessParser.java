import org.apache.pig.builtin.OutputSchema;
import java.io.IOException;
import org.apache.pig.EvalFunc;
import org.apache.pig.data.Tuple;
import org.apache.pig.data.TupleFactory;
import org.apache.pig.data.DataBag;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
@OutputSchema("(business_id:chararray,name:chararray,city:chararray,state:chararray,stars:double,review_count:int,is_open:int,categories:chararray)")
public class YelpBusinessParser extends EvalFunc<Tuple> {

    private static final TupleFactory tupleFactory = TupleFactory.getInstance();

    @Override
    public Tuple exec(Tuple input) throws IOException {

        if (input == null || input.size() == 0 || input.get(0) == null) {
            return null;
        }

        try {
            String json = input.get(0).toString();

            JSONParser parser = new JSONParser();
            JSONObject obj = (JSONObject) parser.parse(json);

            Tuple output = tupleFactory.newTuple(8);

            output.set(0, obj.get("business_id"));
            output.set(1, obj.get("name"));
            output.set(2, obj.get("city"));
            output.set(3, obj.get("state"));
            output.set(4, obj.get("stars"));
            output.set(5, obj.get("review_count"));
            output.set(6, obj.get("is_open"));
            output.set(7, obj.get("categories"));

            return output;

        } catch (Exception e) {
    throw new IOException("JSON parsing failed: " + e.getMessage(), e);
}
    }
}
