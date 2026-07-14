package hipstershop.frontend.money;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import hipstershop.Hipstershop;
import org.junit.jupiter.api.Test;

/** Ports the key cases from the Go frontend's money/money_test.go. */
class MoneyTest {

    private static Hipstershop.Money mmc(long units, int nanos, String currency) {
        return Hipstershop.Money.newBuilder().setUnits(units).setNanos(nanos).setCurrencyCode(currency).build();
    }

    private static Hipstershop.Money mm(long units, int nanos) {
        return mmc(units, nanos, "");
    }

    @Test
    void isValid() {
        assertTrue(Money.isValid(mm(-981273891273L, -999999999)));
        assertFalse(Money.isValid(mm(-981273891273L, 999999999)));
        assertTrue(Money.isValid(mm(981273891273L, 999999999)));
        assertFalse(Money.isValid(mm(981273891273L, -999999999)));
        assertFalse(Money.isValid(mm(3, 1000000000)));
        assertFalse(Money.isValid(mm(3, -1000000000)));
    }

    @Test
    void isZero() {
        assertTrue(Money.isZero(mm(0, 0)));
        assertFalse(Money.isZero(mm(-1, 1)));
    }

    @Test
    void areSameCurrency() {
        assertFalse(Money.areSameCurrency(mmc(1, 0, ""), mmc(2, 0, "")));
        assertFalse(Money.areSameCurrency(mmc(1, 0, "USD"), mmc(2, 0, "CAD")));
        assertTrue(Money.areSameCurrency(mmc(1, 0, "USD"), mmc(2, 0, "USD")));
    }

    @Test
    void areEquals() {
        assertTrue(Money.areEquals(mmc(1, 2, "USD"), mmc(1, 2, "USD")));
        assertFalse(Money.areEquals(mmc(1, 2, "USD"), mmc(1, 2, "CAD")));
        assertFalse(Money.areEquals(mmc(10, 20, "USD"), mmc(1, 20, "USD")));
    }

    @Test
    void negate() {
        assertTrue(Money.areEquals(Money.negate(mm(0, 0)), mm(0, 0)));
        assertTrue(Money.areEquals(Money.negate(mm(-1, -200)), mm(1, 200)));
        assertTrue(Money.areEquals(Money.negate(mmc(0, 0, "XXX")), mmc(0, 0, "XXX")));
    }

    @Test
    void sumMismatchingCurrencyThrows() {
        assertThrows(Money.MismatchingCurrencyException.class, () -> Money.sum(mmc(0, 0, "AAA"), mmc(0, 0, "BBB")));
    }

    @Test
    void sumInvalidValueThrows() {
        assertThrows(Money.InvalidValueException.class, () -> Money.sum(mm(1, -1), mm(0, 0)));
    }

    @Test
    void sumBothPositiveWithCarry() {
        assertEquals(mm(5, 100000000), Money.sum(mm(2, 200000000), mm(2, 900000000)));
    }

    @Test
    void sumBothNegativeWithCarry() {
        assertEquals(mm(-5, -100000000), Money.sum(mm(-2, -200000000), mm(-2, -900000000)));
    }

    @Test
    void sumMixedLargerPositiveWithBorrow() {
        assertEquals(mm(9, 91000000), Money.sum(mm(11, 100000000), mm(-2, -9000000)));
    }

    @Test
    void sumMixedLargerNegativeWithBorrow() {
        assertEquals(mm(-9, -91000000), Money.sum(mm(-11, -100000000), mm(2, 9000000)));
    }

    @Test
    void multiplySlow() {
        assertEquals(mmc(6, 0, "USD"), Money.multiplySlow(mmc(2, 0, "USD"), 3));
    }
}
