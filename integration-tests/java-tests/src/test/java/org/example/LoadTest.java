public class LoadTest {

    private CloseableHttpClient httpClient;
    private String myEnvVariable; // Declare the environment variable here

    @Before
    public void setUp() {
        httpClient = HttpClients.createDefault();
        myEnvVariable = System.getenv("machine_dns"); // Initialize the environment variable
    }

    @After
	@@ -29,7 +31,6 @@ public void tearDown() throws IOException {

    @Test
    public void testIndex() throws IOException {
        HttpGet request = new HttpGet(myEnvVariable);
        HttpResponse response = httpClient.execute(request);
        assertEquals(200, response.getStatusLine().getStatusCode());
	@@ -50,20 +51,13 @@ public void testBrowseProduct() throws IOException {
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
