package com.sap.tamagotchi.controller;

import com.sap.tamagotchi.model.CreateDevicePayload;
import com.sap.tamagotchi.model.Device;
import com.sap.tamagotchi.service.TamagotchiService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.springframework.http.ResponseEntity.ok;

@RestController
public class DeviceController {

    private final TamagotchiService tamagotchiService;

    @Autowired
    public DeviceController(TamagotchiService tamagotchiService) {
        this.tamagotchiService = tamagotchiService;
    }

    @RequestMapping("/devices/{deviceId}")
    public Device getDevice(String deviceId) {
        return tamagotchiService.getDevice(deviceId);
    }

    @RequestMapping("/devices")
    public Collection<Device> getDevices() {
        return tamagotchiService.getDevices();
    }

    @PostMapping("/devices")
    public ResponseEntity createDevice(@RequestBody Collection<CreateDevicePayload> payload) {
        List<Device> devices = new ArrayList<>();
        for (CreateDevicePayload p : payload) {
            devices.add(tamagotchiService.createDevice(new Device(p.getOwner(), p.getColor())));
        }
        return ok(devices);
    }
}
