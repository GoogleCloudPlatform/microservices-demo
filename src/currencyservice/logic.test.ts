import { _carry, convert, Money } from './logic';

describe('logic', () => {
  describe('_carry', () => {
    it('should handle carrying over nanos to units', () => {
      const result = _carry({ units: 1, nanos: 1500000000 });
      expect(result.units).toBe(2);
      expect(result.nanos).toBe(500000000);
    });

    it('should handle fractional units', () => {
      const result = _carry({ units: 1.5, nanos: 0 });
      expect(result.units).toBe(1);
      expect(result.nanos).toBe(500000000);
    });

    it('should handle zero values', () => {
      const result = _carry({ units: 0, nanos: 0 });
      expect(result.units).toBe(0);
      expect(result.nanos).toBe(0);
    });
  });

  describe('convert', () => {
    const currencyData = {
      "EUR": 1,
      "USD": 1.13,
      "JPY": 129.53,
    };

    it('should convert correctly between currencies', () => {
      const from: Money = { currency_code: 'USD', units: 100, nanos: 0 };
      const to_code = 'EUR';
      const result = convert(from, to_code, currencyData);
      expect(result.currency_code).toBe('EUR');
      expect(result.units).toBe(88);
      expect(result.nanos).toBe(495575221);
    });

    it('should throw an error for unsupported currencies', () => {
      const from: Money = { currency_code: 'CAD', units: 100, nanos: 0 };
      const to_code = 'EUR';
      expect(() => convert(from, to_code, currencyData)).toThrow('Unsupported currency');
    });
  });
});
