import express, { Request, Response } from 'express';
import pino from 'pino';
import path from 'path';
import { Money, convert } from './logic';

const logger = pino({
  name: 'currencyservice-server',
  messageKey: 'message',
  formatters: {
    level (logLevelString, logLevelNum) {
      return { severity: logLevelString }
    }
  }
});

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 7000;
const DATA_FILE = path.join(__dirname, '..', 'data', 'currency_conversion.json');

interface ConversionRequest {
  from: Money;
  to_code: string;
}

let currencyData: { [key: string]: number };

try {
  currencyData = require(DATA_FILE);
} catch (err) {
  logger.error(`Failed to load currency data: ${err}`);
  process.exit(1);
}

app.get('/currencies', (req: Request, res: Response) => {
  logger.info('Getting supported currencies...');
  res.json({ currency_codes: Object.keys(currencyData) });
});

app.post('/convert', (req: Request, res: Response) => {
  try {
    const { from, to_code } = req.body as ConversionRequest;
    const result = convert(from, to_code, currencyData);
    logger.info(`Conversion successful: ${from.currency_code} to ${to_code}`);
    res.json(result);
  } catch (err) {
    logger.error(`Conversion failed: ${err}`);
    if (err instanceof Error) {
        res.status(400).json({ error: err.message });
    } else {
        res.status(500).json({ error: 'An unknown error occurred' });
    }
  }
});

app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'SERVING' });
});

app.listen(PORT, () => {
  logger.info(`Currency service listening on port ${PORT}`);
});
