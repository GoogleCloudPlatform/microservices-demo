const path = require('path');

module.exports = {
  entry: './js/index.js',
  output: {
    path: path.resolve(__dirname, 'static/scripts'),
    filename: 'bundle.js',
  },
};
