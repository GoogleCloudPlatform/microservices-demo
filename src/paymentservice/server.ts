// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import express, { Express, Request, Response } from 'express';
import chargeFn, { ChargeRequest, ChargeResponse, CreditCardError } from './charge';
import logger from './logger';

class PaymentServer {
  public app: Express; // Made public for testing access
  private port: string | number;

  public static readonly DEFAULT_PORT: string = '50051'; // Default port if not provided by env

  constructor(port?: string | number) {
    this.port = port || process.env.PORT || PaymentServer.DEFAULT_PORT;
    this.app = express();
    this.app.use(express.json()); // Middleware for parsing JSON bodies
    this.setupRoutes();
  }

  private setupRoutes(): void {
    // POST /charge - Process a payment
    this.app.post('/charge', (req: Request, res: Response) => {
      try {
        const chargeRequest = req.body as ChargeRequest;
        logger.info(`PaymentService#Charge invoked with request ${JSON.stringify(chargeRequest)}`);

        // Basic validation for the request body
        if (!chargeRequest.amount || !chargeRequest.credit_card) {
            return res.status(400).json({ message: 'Missing amount or credit_card details in request.' });
        }
        // Add more specific validation as needed for ChargeRequest properties

        const response = chargeFn(chargeRequest);
        res.status(200).json(response);
      } catch (err: any) {
        logger.warn(`Charge failed: ${err.message}`);
        if (err instanceof CreditCardError) {
          // CreditCardError has a 'code' property, typically 400
          res.status(err.code || 400).json({ message: err.message, errorType: err.name });
        } else {
          // Generic server error
          res.status(500).json({ message: 'An unexpected error occurred during payment processing.', errorType: err.name });
        }
      }
    });

    // GET /health - Health check endpoint
    this.app.get('/health', (req: Request, res: Response) => {
      res.status(200).json({ status: 'SERVING' });
    });
  }

  public listen(): void {
    this.app.listen(this.port, () => {
      logger.info(`PaymentService REST server started on port ${this.port}`);
    }).on('error', (err: Error) => {
      logger.error(`Failed to start PaymentService REST server: ${err.message}`);
    });
  }
}

export default PaymentServer;
