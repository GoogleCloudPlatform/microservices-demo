const pino = require('pino');

module.exports = pino({
  name: 'paymentservice-server',
  messageKey: 'message',
  formatters: {
    level (logLevelString, logLevelNum) {
      return { severity: logLevelString }
    }
  }
});