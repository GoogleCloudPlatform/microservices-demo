// cypress/plugins/index.js

const { registerSealightsTasks } = require('sealights-cypress-plugin');

module.exports = (on, config) => {
  // Set environment variables for your tests here
  config.env.machine_dns = process.env.MACHINE_DNS || 'blabla'; // Use the environment variable if it's set, otherwise use the default value
  registerSealightsTasks(on, config);

  // Log the value of machine_dns (optional)
  console.log('machine_dns:', config.env.machine_dns);

  // Return the updated configuration
  return config;
};
