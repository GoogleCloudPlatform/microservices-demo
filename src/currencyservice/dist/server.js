"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const pino_1 = __importDefault(require("pino"));
const path_1 = __importDefault(require("path"));
const logger = (0, pino_1.default)({
    name: 'currencyservice-server',
    messageKey: 'message',
    formatters: {
        level(logLevelString, logLevelNum) {
            return { severity: logLevelString };
        }
    }
});
const app = (0, express_1.default)();
app.use(express_1.default.json());
const PORT = process.env.PORT || 7000;
const DATA_FILE = path_1.default.join(__dirname, '..', 'data', 'currency_conversion.json');
let currencyData;
try {
    currencyData = require(DATA_FILE);
}
catch (err) {
    logger.error(`Failed to load currency data: ${err}`);
    process.exit(1);
}
function _carry(amount) {
    const fractionSize = Math.pow(10, 9);
    let units = Math.floor(amount.units);
    let nanos = amount.nanos + (amount.units - units) * fractionSize;
    units += Math.floor(nanos / fractionSize);
    nanos = nanos % fractionSize;
    return { units, nanos, currency_code: '' };
}
app.get('/currencies', (req, res) => {
    logger.info('Getting supported currencies...');
    res.json({ currency_codes: Object.keys(currencyData) });
});
app.post('/convert', (req, res) => {
    try {
        const { from, to_code } = req.body;
        if (!currencyData[from.currency_code] || !currencyData[to_code]) {
            return res.status(400).json({ error: 'Unsupported currency' });
        }
        const fromRate = currencyData[from.currency_code];
        const toRate = currencyData[to_code];
        const euros = _carry({
            units: from.units / fromRate,
            nanos: from.nanos / fromRate,
        });
        const result = _carry({
            units: euros.units * toRate,
            nanos: euros.nanos * toRate,
        });
        result.currency_code = to_code;
        logger.info(`Conversion successful: ${from.currency_code} to ${to_code}`);
        res.json(result);
    }
    catch (err) {
        logger.error(`Conversion failed: ${err}`);
        if (err instanceof Error) {
            res.status(500).json({ error: err.message });
        }
        else {
            res.status(500).json({ error: 'An unknown error occurred' });
        }
    }
});
app.get('/health', (req, res) => {
    res.json({ status: 'SERVING' });
});
app.listen(PORT, () => {
    logger.info(`Currency service listening on port ${PORT}`);
});
