/*
 * Copyright 2024 Google LLC
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

package hipstershop;

import hipstershop.Hipstershop.Money;

/**
 * Fixed-point money arithmetic, ported from the Go {@code money} package used by the original
 * checkoutservice. A {@link Money} value is (currency, units, nanos) where nanos are 10^-9 of a
 * unit and must carry the same sign as units. Using integer units/nanos avoids the rounding drift
 * that floating-point currency math introduces.
 */
final class MoneyUtil {

  private static final int NANOS_MIN = -999_999_999;
  private static final int NANOS_MAX = 999_999_999;
  private static final int NANOS_MOD = 1_000_000_000;

  private MoneyUtil() {}

  static class MoneyException extends RuntimeException {
    MoneyException(String message) {
      super(message);
    }
  }

  /** Builds a Money with zero amount in the given currency. */
  static Money zero(String currencyCode) {
    return Money.newBuilder().setCurrencyCode(currencyCode).setUnits(0).setNanos(0).build();
  }

  /** Returns true if the amount is well-formed (valid nanos range, consistent sign). */
  static boolean isValid(Money m) {
    return signMatches(m) && validNanos(m.getNanos());
  }

  private static boolean signMatches(Money m) {
    return m.getNanos() == 0 || m.getUnits() == 0 || (m.getNanos() < 0) == (m.getUnits() < 0);
  }

  private static boolean validNanos(int nanos) {
    return NANOS_MIN <= nanos && nanos <= NANOS_MAX;
  }

  static boolean isZero(Money m) {
    return m.getUnits() == 0 && m.getNanos() == 0;
  }

  static boolean isPositive(Money m) {
    return m.getUnits() > 0 || (m.getUnits() == 0 && m.getNanos() > 0);
  }

  static boolean isNegative(Money m) {
    return m.getUnits() < 0 || (m.getUnits() == 0 && m.getNanos() < 0);
  }

  /** Returns a Money with the amount negated (currency unchanged). */
  static Money negate(Money m) {
    return Money.newBuilder()
        .setCurrencyCode(m.getCurrencyCode())
        .setUnits(-m.getUnits())
        .setNanos(-m.getNanos())
        .build();
  }

  /**
   * Adds two Money values of the same currency, normalizing the units/nanos carry and sign. Mirrors
   * {@code money.Sum} in the Go implementation.
   */
  static Money sum(Money l, Money r) {
    if (!isValid(l) || !isValid(r)) {
      throw new MoneyException("one of the specified money values is invalid");
    }
    if (!l.getCurrencyCode().equals(r.getCurrencyCode())) {
      throw new MoneyException("mismatching currency codes");
    }

    long units = l.getUnits() + r.getUnits();
    int nanos = l.getNanos() + r.getNanos();

    if ((units == 0 && nanos == 0) || (units > 0 && nanos >= 0) || (units < 0 && nanos <= 0)) {
      // Same sign: fold any nanos overflow into units.
      units += nanos / NANOS_MOD;
      nanos = nanos % NANOS_MOD;
    } else {
      // Opposite signs: borrow one unit so units and nanos agree in sign.
      if (units > 0) {
        units--;
        nanos += NANOS_MOD;
      } else {
        units++;
        nanos -= NANOS_MOD;
      }
    }

    return Money.newBuilder()
        .setCurrencyCode(l.getCurrencyCode())
        .setUnits(units)
        .setNanos(nanos)
        .build();
  }

  /**
   * Multiplies a Money value by a non-negative integer via repeated addition, matching {@code
   * money.MultiplySlow}. Quantities are small (per-line cart quantities), so this is not a hot path.
   */
  static Money multiplySlow(Money m, long factor) {
    Money out = zero(m.getCurrencyCode());
    for (long i = 0; i < factor; i++) {
      out = sum(out, m);
    }
    return out;
  }
}
