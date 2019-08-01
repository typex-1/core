const path = require('path');

module.exports = {
  entry: {
    genpk: './unpack/genpk.js',
    trace: './unpack/trace.js',
  },
  output: {
    publicPath: './js/',
    path: path.resolve(__dirname, './static/js/'),
    filename: '[name].js'
  }
}
