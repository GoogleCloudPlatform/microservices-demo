package com.sap.tamagotchi.service;

import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.publisher.PublisherService;

@Service
@EnableScheduling
public class TamagotchiService {

    private static final long DEVICE_EVENT_PROCESSOR_SCHEDULE = 5_000;

    private final Logger logger;

    private final PublisherService publisherService;

    private final Map<String, Device> deviceRegistry = Collections.synchronizedMap(new HashMap<>());

    @Autowired
    public TamagotchiService(PublisherService publisherService, Logger logger) {
        this.publisherService = publisherService;
        this.logger = logger;
    }

    public Device getDevice(String deviceId) {
        return deviceRegistry.get(deviceId);
    }

    public Collection<Device> getDevices() {
        return deviceRegistry.values();
    }

    public Set<String> getDeviceIds() {
        return deviceRegistry.keySet();
    }

    public Device createDevice(Device device) {
        device.start();
        deviceRegistry.put(device.getDeviceId(), device);
        return device;
    }

    @Scheduled(fixedDelay = DEVICE_EVENT_PROCESSOR_SCHEDULE)
    private void processDeviceEvents() {
        deviceRegistry
                .values()
                .parallelStream()
                .filter(device -> device.hasMessages())
                .flatMap(device -> device.getMessages().stream())
                .forEach(message -> {
                    try {
                        publisherService.publish(message);
                    } catch (Exception ex) {
                        logger.error("processing device events failed: {}", ex.getMessage());
                        throw new RuntimeException(ex);
                    }
                });
    }
}
