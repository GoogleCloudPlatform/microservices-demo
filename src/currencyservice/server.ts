/*
 * Copyright 2018 Google LLC.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import pino from 'pino';
import express, { Request, Response } from 'express';
// import { GrpcInstrumentation } from '@opentelemetry/instrumentation-grpc'; // Not needed for REST
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { ExpressInstrumentation } from '@opentelemetry/instrumentation-express';
import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node';
import { SimpleSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-otlp-grpc';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

interface Money {
  currency_code: string;
  units: number;
  nanos: number;
}

interface CurrencyConversionRequest {
  from: Money;
  to_code: string;
}

// GetSupportedCurrenciesResponse is implicitly an array of strings, e.g., string[]

const logger = pino({
  name: 'currencyservice-server',
  messageKey: 'message',
  formatters: {
    level(logLevelString: string, logLevelNum: number) {
      return { severity: logLevelString };
    },
  },
});

if (process.env.DISABLE_PROFILER) {
  logger.info('Profiler disabled.');
} else {
  logger.info('Profiler enabled.');
  require('@google-cloud/profiler').start({
    serviceContext: {
      service: 'currencyservice',
      version: '1.0.0',
    },
  });
}

// Register OpenTelemetry instrumentation for HTTP and Express
registerInstrumentations({
  instrumentations: [
    new HttpInstrumentation(),
    new ExpressInstrumentation(),
  ],
});

if (process.env.ENABLE_TRACING === '1') {
  logger.info('Tracing enabled.');
  const provider = new NodeTracerProvider({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: process.env.OTEL_SERVICE_NAME || 'currencyservice',
    }),
  });

  const collectorUrl = process.env.COLLECTOR_SERVICE_ADDR;
  if (collectorUrl) {
    provider.addSpanProcessor(new SimpleSpanProcessor(new OTLPTraceExporter({ url: collectorUrl })));
    provider.register();
  } else {
    logger.warn('Collector service address not set. Tracing will not be exported.');
  }
} else {
  logger.info('Tracing disabled.');
}

const PORT = process.env.PORT || '7000';
const app = express();
app.use(express.json()); // Middleware to parse JSON bodies

// Export app for testing purposes
export { app };

interface CurrencyData {
  [currencyCode: string]: number;
}

let currencyDataInstance: CurrencyData | null = null;

// Helper function to load currency data (once)
function getCurrencyData(): CurrencyData {
  if (!currencyDataInstance) {
    currencyDataInstance = require('./data/currency_conversion.json') as CurrencyData;
  }
  return currencyDataInstance;
}


function _carry(amount: Money): Money {
  const fractionSize = Math.pow(10, 9);
  amount.nanos += (amount.units % 1) * fractionSize;
  amount.units = Math.floor(amount.units) + Math.floor(amount.nanos / fractionSize);
  amount.nanos = amount.nanos % fractionSize;
  return amount;
}

// GET /currencies - Lists the supported currencies
app.get('/currencies', (req: Request, res: Response) => {
  logger.info('Getting supported currencies...');
  try {
    const data = getCurrencyData();
    res.json(Object.keys(data));
  } catch (error) {
    logger.error(`Failed to get supported currencies: ${error instanceof Error ? error.message : String(error)}`);
    res.status(500).send('Error fetching currency data');
  }
});

// POST /convert - Converts between currencies
app.post('/convert', (req: Request, res: Response) => {
  try {
    const { from, to_code } = req.body as CurrencyConversionRequest;
    logger.info(`Conversion request: ${JSON.stringify(req.body)}`);

    if (!from || typeof from.currency_code !== 'string' || typeof from.units !== 'number' || typeof from.nanos !== 'number' || typeof to_code !== 'string') {
      return res.status(400).send('Invalid request body for currency conversion.');
    }

    const data = getCurrencyData();

    if (!data[from.currency_code] || !data[to_code]) {
      return res.status(400).json({ message: 'Unsupported currency code.' });
    }

    const euros = _carry({
      units: from.units / data[from.currency_code],
      nanos: from.nanos / data[from.currency_code],
      currency_code: 'EUR',
    });

    euros.nanos = Math.round(euros.nanos);

    const result = _carry({
      units: euros.units * data[to_code],
      nanos: euros.nanos * data[to_code],
      currency_code: to_code,
    });

    result.units = Math.floor(result.units);
    result.nanos = Math.floor(result.nanos);

    logger.info('conversion request successful');
    res.json(result);
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err);
    logger.error(`conversion request failed: ${errorMessage}`);
    res.status(500).json({ message: 'An error occurred during currency conversion', error: errorMessage });
  }
});

// GET /health - Endpoint for health checks
app.get('/health', (req: Request, res: Response) => {
  res.json({ status: 'SERVING' });
});

function main(): void {
  // Only start listening if the script is run directly
  if (require.main === module) {
    app.listen(PORT, () => {
      logger.info(`CurrencyService REST server started on port ${PORT}`);
    });
  }
}

main();

// Export the main function if you need to start server programmatically for integration tests,
// but for unit tests, importing `app` is usually sufficient.
// export { main as startServer };
