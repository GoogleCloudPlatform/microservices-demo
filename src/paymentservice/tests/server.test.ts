import request from 'supertest';
// Assuming server.ts will be refactored to export its Express app instance
// import { app } from '../server'; // This will be the goal
import PaymentServer from '../server'; // Import the class
import express from 'express'; // For type annotation

let app: express.Application; // Will be instance from PaymentServer

// Mock pino logger
jest.mock('../logger', () => {
  const pinoMock = jest.fn(() => ({
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
    fatal: jest.fn(),
    trace: jest.fn(),
    silent: jest.fn(),
    child: jest.fn().mockReturnThis(),
  }));
  return {
    __esModule: true, // This is important for ES modules
    default: pinoMock(), // If logger.ts uses export default
  };
});


// Mock charge.ts
const mockChargeFn = jest.fn();
jest.mock('../charge', () => ({
  __esModule: true,
  default: mockChargeFn, // If charge.ts uses export default
  CreditCardError: class extends Error { code = 400; constructor(msg: string) { super(msg); this.name = 'CreditCardError';}},
  InvalidCreditCard: class extends Error { code = 400; constructor(msg?: string) { super(msg || 'InvCard'); this.name = 'InvalidCreditCard';}},
  UnacceptedCreditCard: class extends Error { code = 400; constructor(msg?: string) { super(msg || 'UnaccCard'); this.name = 'UnacceptedCreditCard';}},
  ExpiredCreditCard: class extends Error { code = 400; constructor(msg?: string) { super(msg || 'ExpCard'); this.name = 'ExpiredCreditCard';}},
}));


describe('Payment Service API', () => {
  beforeAll(() => {
    const serverInstance = new PaymentServer('0'); // Use ephemeral port for testing
    app = serverInstance.app; // Access the public app instance
  });

  beforeEach(() => {
    // Reset mocks before each test
    mockChargeFn.mockReset();
  });

  describe('POST /charge', () => {
    const validChargeRequest = {
      amount: { currency_code: 'USD', units: 100, nanos: 0 },
      credit_card: {
        credit_card_number: '4000000000000000', // Visa
        credit_card_cvv: 123,
        credit_card_expiration_year: new Date().getFullYear() + 1,
        credit_card_expiration_month: 12,
      },
    };

    it('should process a valid payment and return a transaction ID', async () => {
      const mockTransactionId = 'mock-transaction-id';
      mockChargeFn.mockReturnValue({ transaction_id: mockTransactionId });

      const response = await request(app)
        .post('/charge')
        .send(validChargeRequest);

      expect(response.status).toBe(200);
      expect(response.body).toEqual({ transaction_id: mockTransactionId });
      expect(mockChargeFn).toHaveBeenCalledWith(validChargeRequest);
    });

    it('should return 400 if charge function throws InvalidCreditCard', async () => {
      mockChargeFn.mockImplementation(() => {
        const error = new Error("Invalid card") as any;
        error.name = "InvalidCreditCard";
        error.code = 400;
        throw error;
      });
      const response = await request(app)
        .post('/charge')
        .send(validChargeRequest);
      expect(response.status).toBe(400);
      expect(response.body.errorType).toBe('InvalidCreditCard');
    });

    it('should return 400 for an unaccepted credit card type', async () => {
        mockChargeFn.mockImplementation(() => {
            const error = new Error("Unaccepted card type") as any;
            error.name = "UnacceptedCreditCard";
            error.code = 400;
            throw error;
        });
        const response = await request(app).post('/charge').send({
            ...validChargeRequest,
            credit_card: { ...validChargeRequest.credit_card, credit_card_number: '6011000000000000' } // Discover (example)
        });
        expect(response.status).toBe(400);
        expect(response.body.errorType).toBe('UnacceptedCreditCard');
    });

    it('should return 400 for an expired credit card', async () => {
        mockChargeFn.mockImplementation(() => {
            const error = new Error("Expired card") as any;
            error.name = "ExpiredCreditCard";
            error.code = 400;
            throw error;
        });
        const response = await request(app).post('/charge').send({
            ...validChargeRequest,
            credit_card: { ...validChargeRequest.credit_card, credit_card_expiration_year: 2020 }
        });
        expect(response.status).toBe(400);
        expect(response.body.errorType).toBe('ExpiredCreditCard');
    });

    it('should return 400 for missing amount', async () => {
      const { amount, ...incompleteRequest } = validChargeRequest;
      const response = await request(app)
        .post('/charge')
        .send(incompleteRequest);
      // The actual status code might depend on how the dummy/actual app handles this
      // For now, assuming the mock or basic validation in dummy app might not catch this as 400 unless chargeFn does
      // This test will be more robust when testing the actual app's validation
      // If chargeFn is not called due to app-level validation, this test might need adjustment.
      // For now, we assume the call reaches the point where chargeFn would be invoked or its mock.
      // If the dummy app's simplified route doesn't do this validation, this test might pass with 200 if mockChargeFn is too simple.
      // Let's assume the error is thrown by mockChargeFn if data is incomplete.
      mockChargeFn.mockImplementation(() => {
        const error = new Error("Missing amount") as any;
        error.name = "CreditCardError"; // Generic error for bad request
        error.code = 400;
        throw error;
      });
       expect(response.status).toBe(400); // This depends on actual app validation
    });


    it('should return 500 if charge function throws an unexpected error', async () => {
      mockChargeFn.mockImplementation(() => {
        throw new Error('Unexpected internal error');
      });
      const response = await request(app)
        .post('/charge')
        .send(validChargeRequest);
      expect(response.status).toBe(500);
    });
  });

  describe('GET /health', () => {
    it('should return SERVING status', async () => {
      const response = await request(app).get('/health');
      expect(response.status).toBe(200);
      expect(response.body).toEqual({ status: 'SERVING' });
    });
  });
});
