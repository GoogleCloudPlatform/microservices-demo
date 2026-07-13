package hipstershop.frontend.web;

import org.springframework.stereotype.Component;

/**
 * Mirrors the Go frontend's package-level {@code plat platformDetails} var in
 * handlers.go: only the home page handler ever recomputes it; every other
 * page simply reads whatever value was last computed there.
 */
@Component
public class PlatformDetailsHolder {

    private volatile PlatformDetails current = new PlatformDetails("", "");

    public PlatformDetails get() {
        return current;
    }

    public void set(PlatformDetails details) {
        this.current = details;
    }
}
