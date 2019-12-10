package com.sap.tamagotchi.controller;

import java.util.Collection;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.service.TamagotchiService;

@RestController
public class DeviceController {

    private static final String template = "Hello !!!!!, %s!";
    private final AtomicLong counter = new AtomicLong();
    private final TamagotchiService tamagotchiService;

    @Autowired
    public DeviceController(TamagotchiService tamagotchiService) {
        this.tamagotchiService = tamagotchiService;
    }

    @RequestMapping("devices/{deviceId}")
    public Device getDevice(String deviceId) {
        return tamagotchiService.getDevice(deviceId);
    }

    @RequestMapping("devices")
    public Collection<Device> getDevices() {
        return tamagotchiService.getDevices();
    }
    // TODO postmapping create
    // request payload
    // owner String
    // color
}
