// cypress/plugins/index.js

module.exports = (on, config) => {
  // Set environment variables for your tests here
  config.env.machine_dns ='http://dev-ahmad-branch-1-0-159.dev.sealights.co:8081';

  // Return the updated configuration
  return config;
};
