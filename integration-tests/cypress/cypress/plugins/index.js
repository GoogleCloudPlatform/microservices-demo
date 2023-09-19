// cypress/plugins/index.js


const { registerSealightsTasks } = require('SL.Cypress.Plugin/dist/code-coverage/config');

module.exports = (on, config) => {
  // Set environment variables for your tests here
 config.env.machine_dns = 'http://10.2.10.50:8081';
 registerSealightsTasks(on, config);
  // Return the updated configuration
  return config;
};
