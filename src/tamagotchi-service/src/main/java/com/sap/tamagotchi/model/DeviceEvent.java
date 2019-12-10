package com.sap.tamagotchi.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;

public class DeviceEvent implements IoTMessage {

    @JsonProperty("id")
    private final String id;
    @JsonProperty("owner")
    private final String owner;
    @JsonProperty("color")
    private final Color color;
    @JsonProperty("born")
    private final Instant born;
    @JsonProperty("healthScore")
    private final Integer healthScore;
    @JsonProperty("eventTime")
    private final Instant eventTime;

    public DeviceEvent(String id, String owner, Color color, Instant born, Integer healthScore, Instant eventTime) {
        this.id = id;
        this.owner = owner;
        this.color = color;
        this.born = born;
        this.healthScore = healthScore;
        this.eventTime = eventTime;
    }

    @JsonProperty("id")
    public String getId() {
        return id;
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
    public Instant getBorn() {
        return born;
    }

    @JsonProperty("healthScore")
    public Integer getHealthScore() {
        return healthScore;
    }

    @JsonProperty("eventTime")
    public Instant getEventTime() {
        return eventTime;
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
