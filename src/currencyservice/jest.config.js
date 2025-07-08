module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
  moduleNameMapper: {
    // Handle module aliases (if you have them in tsconfig.json)
    // Example: '^@/(.*)$': '<rootDir>/src/$1'
  },
  // Automatically clear mock calls and instances between every test
  clearMocks: true,
  // Indicates whether the coverage information should be collected while executing the test
  collectCoverage: true,
  // The directory where Jest should output its coverage files
  coverageDirectory: 'coverage',
  // An array of glob patterns indicating a set of files for which coverage information should be collected
  collectCoverageFrom: ['src/**/*.ts'],
};
