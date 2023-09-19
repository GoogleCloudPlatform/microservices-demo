// cypress/support/commands.js

Cypress.Commands.add('apiRequest', (method, url, data = {}, options = {}) => {
  return cy.request({
    method,
    url: Cypress.env('machine_dns') + url,
    body: data,
    ...options,
  });
});
