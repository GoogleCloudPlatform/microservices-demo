import request from 'supertest';
// Assuming your Express app is exported from server.ts,
// you might need to refactor server.ts to export the app for testing,
// or start the server in a beforeEach and close it in an afterEach.
// For simplicity, let's assume server.ts exports the app directly or via a getter.
// This will likely require a small refactor of server.ts if it immediately calls app.listen().

// A common pattern is to have `app.ts` define and export the app,
// and `server.ts` import app and call listen.
import { app } from '../server'; // Import the actual app
import express from 'express'; // For Express.Application type, though app is already configured

// Mock pino logger to prevent test output from being cluttered with logs
jest.mock('pino', () => {
  const pinoMock = jest.fn(() => ({
    info: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn(),
    fatal: jest.fn(),
    trace: jest.fn(),
    silent: jest.fn(),
    child: jest.fn().mockReturnThis(), // Ensure child() returns the mock for chained calls
  }));
  return pinoMock;
});


describe('Currency Service API', () => {
  // app is now imported directly, so no need for beforeAll setup of a dummy app.

  describe('GET /currencies', () => {
    it('should return a list of supported currency codes', async () => {
      const response = await request(app).get('/currencies');
      expect(response.status).toBe(200);
      expect(response.body).toBeInstanceOf(Array);
      expect(response.body).toContain('USD');
      expect(response.body).toContain('EUR');
    });
  });

  describe('POST /convert', () => {
    it('should convert an amount from one currency to another', async () => {
      const conversionRequest = {
        from: { currency_code: 'USD', units: 100, nanos: 0 },
        to_code: 'EUR',
      };
      const response = await request(app)
        .post('/convert')
        .send(conversionRequest);
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('currency_code', 'EUR');
      expect(response.body).toHaveProperty('units');
      expect(response.body).toHaveProperty('nanos');
    });

    it('should return 400 for unsupported "from" currency', async () => {
      const conversionRequest = {
        from: { currency_code: 'XYZ', units: 100, nanos: 0 },
        to_code: 'EUR',
      };
      const response = await request(app)
        .post('/convert')
        .send(conversionRequest);
      expect(response.status).toBe(400);
    });

    it('should return 400 for unsupported "to" currency', async () => {
      const conversionRequest = {
        from: { currency_code: 'USD', units: 100, nanos: 0 },
        to_code: 'XYZ',
      };
      const response = await request(app)
        .post('/convert')
        .send(conversionRequest);
      expect(response.status).toBe(400);
    });

    it('should return 400 for invalid request body', async () => {
      const response = await request(app)
        .post('/convert')
        .send({ from: { units: 100 }, to_code: 'EUR' }); // Missing currency_code and nanos
      expect(response.status).toBe(400);
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
