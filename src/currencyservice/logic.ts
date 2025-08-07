export interface Money {
  currency_code: string;
  units: number;
  nanos: number;
}

export function _carry(amount: { units: number; nanos: number }): Money {
  const fractionSize = 10 ** 9;
  let units = Math.floor(amount.units);
  let nanos = amount.nanos + (amount.units - units) * fractionSize;

  units += Math.floor(nanos / fractionSize);
  nanos = nanos % fractionSize;
  nanos = Math.round(nanos);

  return { units, nanos, currency_code: '' };
}

export function convert(from: Money, to_code: string, currencyData: { [key: string]: number }): Money {
  if (!currencyData[from.currency_code] || !currencyData[to_code]) {
    throw new Error('Unsupported currency');
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
  return result;
}
