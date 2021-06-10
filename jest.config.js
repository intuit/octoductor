module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testPathIgnorePatterns:  [
    "cdk.out"
  ],
  maxConcurrency: 12,
  coverageReporters: ['html', 'json'],
  collectCoverage: true,
  coverageDirectory: './.coverage',
  testMatch: ['**/*.test.ts'],
};
