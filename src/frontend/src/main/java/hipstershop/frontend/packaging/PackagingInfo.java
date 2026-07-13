package hipstershop.frontend.packaging;

/** Mirrors the Go frontend's {@code PackagingInfo} struct in packaging_info.go. */
public class PackagingInfo {
    private float weight;
    private float width;
    private float height;
    private float depth;

    public float getWeight() {
        return weight;
    }

    public void setWeight(float weight) {
        this.weight = weight;
    }

    public float getWidth() {
        return width;
    }

    public void setWidth(float width) {
        this.width = width;
    }

    public float getHeight() {
        return height;
    }

    public void setHeight(float height) {
        this.height = height;
    }

    public float getDepth() {
        return depth;
    }

    public void setDepth(float depth) {
        this.depth = depth;
    }
}
