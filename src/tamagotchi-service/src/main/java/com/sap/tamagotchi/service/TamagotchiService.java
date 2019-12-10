package com.sap.tamagotchi.service;

import com.sap.tamagotchi.model.Device;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

@Service
public class TamagotchiService {

    private final Map<String, Device> deviceRegistry = new HashMap<>();

    public Device getDevice(String deviceId) {
        return deviceRegistry.get(deviceId);
    }

    public Collection<Device> getDevices() {
        return deviceRegistry.values();
    }
}
