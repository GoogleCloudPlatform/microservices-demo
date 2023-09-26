exports.config = {
  // Specify the address of your running Angular application.
  baseUrl: 'http://10.2.10.50:8081',

  // Framework to use. Jasmine is a popular choice.
  framework: 'jasmine',

  // Path to your Protractor test files (specs).
  specs: ['tests/api-tests.js'],

  // MultiCapabilities allows you to run tests on multiple browsers.
  multiCapabilities: [
    {
      browserName: 'chrome',
      // Other browser-specific configuration options can be added here.
    },
    // Add more capabilities for other browsers if needed.
  ],

  // Jasmine options.
  jasmineNodeOpts: {
    defaultTimeoutInterval: 30000, // Adjust this as needed.
  },

  // Specifying which reporter to use for test results.
  // You can add more reporters or customize the configuration as needed.
  reporters: ['spec'],

  // Additional options can be added here as per your project requirements.

  // Configure the Selenium Server address, if not using Protractor's built-in WebDriver.
  // seleniumAddress: 'http://localhost:4444/wd/hub',
};
