module.exports = {
  projects: [
    {
      name: 'chrome',
      use: { ...require('@playwright/test').devices['Desktop Chrome'] },
      reporter: [['list'], ['json', { outputFile: 'results.json' }]],
      retries: 0,
      testMatch: '**/*.spec.js',
    },
  ],
};
