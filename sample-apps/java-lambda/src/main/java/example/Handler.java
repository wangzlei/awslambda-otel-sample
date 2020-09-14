package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import org.apache.http.HttpEntity;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import java.util.Map;

public class Handler implements RequestHandler<Map<String,String>, String> {

    public String handleRequest(Map<String,String> event, Context context)
    {
        LambdaLogger logger = context.getLogger();

        String response = "200 OK";

        logger.log("AWS Lambda OpenTelemetry integration Sample.");

        int i = 10;
        while(--i >= 0)
        {
            httpCall(contect);
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        return response;
    }

    private static void httpCall(Context context) {
        LambdaLogger logger = context.getLogger();
        try (CloseableHttpClient httpclient = HttpClients.createDefault()) {
            HttpGet httpget = new HttpGet("http://httpbin.org/");

            logger.log("Executing request " + httpget.getRequestLine());

            // Create a custom response handler
            ResponseHandler<String> responseHandler = response -> {
                int status = response.getStatusLine().getStatusCode();
                if (status >= 200 && status < 300) {
                    HttpEntity entity = response.getEntity();
                    return entity != null ? EntityUtils.toString(entity) : null;
                } else {
                    throw new ClientProtocolException("Unexpected response status: " + status);
                }
            };
            httpclient.execute(httpget, responseHandler);
            logger.log("----------------------------------------");
        }
    }

}
