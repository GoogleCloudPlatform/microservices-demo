package hipstershop.frontend.web;

/** Mirrors the Go frontend's {@code platformDetails} struct in handlers.go. */
public record PlatformDetails(String css, String provider) {

    public static PlatformDetails forEnv(String env) {
        return switch (env) {
            case "aws" -> new PlatformDetails("aws-platform", "AWS");
            case "onprem" -> new PlatformDetails("onprem-platform", "On-Premises");
            case "azure" -> new PlatformDetails("azure-platform", "Azure");
            case "gcp" -> new PlatformDetails("gcp-platform", "Google Cloud");
            case "alibaba" -> new PlatformDetails("alibaba-platform", "Alibaba Cloud");
            default -> new PlatformDetails("local", "local");
        };
    }
}
