package com.sap.tamagotchi.controller;

import com.sap.tamagotchi.model.CreateDevicePayload;
import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.service.TamagotchiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Collection;

import static org.springframework.http.ResponseEntity.ok;

@RestController
public class DeviceController {

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

    @PostMapping
    public ResponseEntity createDevice(CreateDevicePayload payload) {
        return ok(tamagotchiService.createDevice(new Device(payload.getOwner(), payload.getColor()))).build();
    }
}
