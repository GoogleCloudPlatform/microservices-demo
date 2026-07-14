package hipstershop.frontend.money;

import hipstershop.Hipstershop;

/**
 * Money arithmetic helpers, a straight port of the Go frontend's {@code money.go}.
 * Values are represented as {@link Hipstershop.Money} (units + nanos + currency code),
 * matching the wire type shared across all services.
 */
public final class Money {

    private static final int NANOS_MIN = -999999999;
    private static final int NANOS_MAX = 999999999;
    private static final int NANOS_MOD = 1000000000;

    private Money() {
    }

    public static class MismatchingCurrencyException extends RuntimeException {
        public MismatchingCurrencyException() {
            super("mismatching currency codes");
        }
    }

    public static class InvalidValueException extends RuntimeException {
        public InvalidValueException() {
            super("one of the specified money values is invalid");
        }
    }

    public static boolean isValid(Hipstershop.Money m) {
        return signMatches(m) && validNanos(m.getNanos());
    }

    private static boolean signMatches(Hipstershop.Money m) {
        return m.getNanos() == 0 || m.getUnits() == 0 || ((m.getNanos() < 0) == (m.getUnits() < 0));
    }

    private static boolean validNanos(int nanos) {
        return NANOS_MIN <= nanos && nanos <= NANOS_MAX;
    }

    public static boolean isZero(Hipstershop.Money m) {
        return m.getUnits() == 0 && m.getNanos() == 0;
    }

    public static boolean areSameCurrency(Hipstershop.Money l, Hipstershop.Money r) {
        return l.getCurrencyCode().equals(r.getCurrencyCode()) && !l.getCurrencyCode().isEmpty();
    }

    public static boolean areEquals(Hipstershop.Money l, Hipstershop.Money r) {
        return l.getCurrencyCode().equals(r.getCurrencyCode())
                && l.getUnits() == r.getUnits()
                && l.getNanos() == r.getNanos();
    }

    public static Hipstershop.Money negate(Hipstershop.Money m) {
        return Hipstershop.Money.newBuilder()
                .setUnits(-m.getUnits())
                .setNanos(-m.getNanos())
                .setCurrencyCode(m.getCurrencyCode())
                .build();
    }

    /** Adds two values. Throws if either value is invalid or currency codes mismatch. */
    public static Hipstershop.Money sum(Hipstershop.Money l, Hipstershop.Money r) {
        if (!isValid(l) || !isValid(r)) {
            throw new InvalidValueException();
        }
        if (!l.getCurrencyCode().equals(r.getCurrencyCode())) {
            throw new MismatchingCurrencyException();
        }

        long units = l.getUnits() + r.getUnits();
        int nanos = l.getNanos() + r.getNanos();

        if ((units == 0 && nanos == 0) || (units > 0 && nanos >= 0) || (units < 0 && nanos <= 0)) {
            // same sign <units, nanos>
            units += nanos / NANOS_MOD;
            nanos = nanos % NANOS_MOD;
        } else {
            // different sign. nanos guaranteed to not to go over the limit
            if (units > 0) {
                units--;
                nanos += NANOS_MOD;
            } else {
                units++;
                nanos -= NANOS_MOD;
            }
        }

        return Hipstershop.Money.newBuilder()
                .setUnits(units)
                .setNanos(nanos)
                .setCurrencyCode(l.getCurrencyCode())
                .build();
    }

    /** Slow multiplication done through repeated addition, matching the Go implementation exactly. */
    public static Hipstershop.Money multiplySlow(Hipstershop.Money m, long n) {
        Hipstershop.Money out = m;
        while (n > 1) {
            out = sum(out, m);
            n--;
        }
        return out;
    }
}
