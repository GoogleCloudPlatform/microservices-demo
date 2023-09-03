// cypress/plugins/index.js

module.exports = (on, config) => {
  // Set environment variables for your tests here
  config.env.machine_dns = 'http://10.2.10.163:8081';

  // Return the updated configuration
  return config;
};
