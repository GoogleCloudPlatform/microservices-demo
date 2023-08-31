package org.example;

import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.io.IOException;
import java.util.Random;

import static org.junit.Assert.assertEquals;

public class LoadTest {

    private CloseableHttpClient httpClient;
    private String myEnvVariable; // Declare the environment variable here

    @Before
    public void setUp() {
        httpClient = HttpClients.createDefault();
        myEnvVariable = System.getenv("machine_dns"); // Initialize the environment variable
    }

    @After
    public void tearDown() throws IOException {
        httpClient.close();
    }

    @Test
    public void testIndex() throws IOException {
        HttpGet request = new HttpGet(myEnvVariable);
        HttpResponse response = httpClient.execute(request);
        assertEquals(200, response.getStatusLine().getStatusCode());
    }

    @Test
    public void testSetCurrency() throws IOException {
        String[] currencies = {"EUR", "USD", "JPY", "CAD"};
        String currency = currencies[new Random().nextInt(currencies.length)];

        HttpGet request = new HttpGet(myEnvVariable + "/setCurrency?currency_code=" + currency);
        HttpResponse response = httpClient.execute(request);
        assertEquals(405, response.getStatusLine().getStatusCode());
    }

    @Test
    public void testBrowseProduct() throws IOException {
        String[] products = {
            "0PUK6V6EV0",
            "1YMWWN1N4O",
            // ... rest of the products
        };

        String product = products[new Random().nextInt(products.length)];

        HttpGet request = new HttpGet(myEnvVariable + "/product/" + product);
        HttpResponse response = httpClient.execute(request);
        assertEquals(200, response.getStatusLine().getStatusCode());
    }
}
