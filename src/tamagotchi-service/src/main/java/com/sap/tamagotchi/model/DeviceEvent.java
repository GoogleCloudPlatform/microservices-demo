package com.sap.tamagotchi.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;


public class DeviceEvent implements IoTMessage {

    @JsonProperty("id")
    private final String id;
    @JsonProperty("productId")
    private final String productId;
    @JsonProperty("owner")
    private final String owner;
    @JsonProperty("color")
    private final Color color;
    @JsonProperty("born")
    private final Instant born;
    @JsonProperty("healthScore")
    private final Integer healthScore;
    @JsonProperty("lastHealthScore")
    private final Integer lastHealthScore;
    @JsonProperty("eventTime")
    private final Instant eventTime;

    public DeviceEvent(String id, String productId, String owner, Color color, Instant born, Integer healthScore, Integer lastHealthScore, Instant eventTime) {
        this.id = id;
        this.productId = productId;
        this.owner = owner;
        this.color = color;
        this.born = born;
        this.healthScore = healthScore;
        this.lastHealthScore = lastHealthScore;
        this.eventTime = eventTime;
    }

    @JsonProperty("id")
    public String getId() {
        return id;
    }

    @JsonProperty("productId")
    public String getProductId() {
        return productId;
    }

    @JsonProperty("owner")
    public String getOwner() {
        return owner;
    }

    @JsonProperty("color")
    public Color getColor() {
        return color;
    }

    @JsonProperty("born")
    public String getBorn() {
        return born.toString();
    }

    @JsonProperty("healthScore")
    public Integer getHealthScore() {
        return healthScore;
    }

    @JsonInclude(JsonInclude.Include.NON_NULL)
    @JsonProperty("lastHealthScore")
    public Integer getLastHealthScore() {
        return lastHealthScore;
    }

    @JsonProperty("eventTime")
    public String getEventTime() {
        return eventTime.toString();
    }

    @JsonProperty("isAlive")
    public boolean isAlive() {
        return healthScore > 1;
    }

    @JsonIgnore
    @Override
    public String getTopic() {
        return "tamagotchi-events";
    }

    @Override
    public String toString() {
        return "DeviceEvent{" +
                "id='" + id + '\'' +
                ", owner='" + owner + '\'' +
                ", color=" + color +
                ", born=" + born +
                ", healthScore=" + healthScore +
                ", eventTime=" + eventTime +
                '}';
    }
}
