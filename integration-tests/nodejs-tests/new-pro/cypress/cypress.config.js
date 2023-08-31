const { defineConfig } = require("cypress");
const registerSealights =
    require("SL.Cypress.Plugin/dist/code-coverage/config").default;

module.exports = defineConfig({
    e2e: {
        experimentalInteractiveRunEvents: true, // If you want to run with 'npm cypress open' and still report coverage
        setupNodeEvents(on, config) {
            registerSealights(on, config);
        },
    },
});
