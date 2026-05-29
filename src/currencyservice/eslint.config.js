import globals from 'globals';
import google from 'eslint-config-google';

export default [
  {
    ignores: ['node_modules/**'],
  },
  google, // Include the google config here
  {
    files: ['**/*.js'],
    languageOptions: {
      globals: globals.node,
      ecmaVersion: 2021,
    },
    rules: {
      'require-jsdoc': 'off',
      'valid-jsdoc': 'off',
    },
  },
];
