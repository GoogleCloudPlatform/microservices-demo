package hipstershop.frontend.web;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

/** Ports {@code logoutHandler} and the misc inline routes from main.go. */
@Controller
public class MiscController {

    private static final Logger log = LoggerFactory.getLogger(MiscController.class);

    @GetMapping("/logout")
    public String logout(HttpServletRequest request, HttpServletResponse response) {
        log.debug("logging out");
        Cookie[] cookies = request.getCookies();
        if (cookies != null) {
            for (Cookie c : cookies) {
                Cookie expired = new Cookie(c.getName(), "");
                expired.setMaxAge(0);
                expired.setPath("/");
                response.addCookie(expired);
            }
        }
        return "redirect:/";
    }

    @GetMapping(value = "/robots.txt", produces = MediaType.TEXT_PLAIN_VALUE)
    @ResponseBody
    public String robots() {
        return "User-agent: *\nDisallow: /";
    }

    @GetMapping(value = "/_healthz", produces = MediaType.TEXT_PLAIN_VALUE)
    @ResponseBody
    public String healthz() {
        return "ok";
    }
}
