/**
 * Copyright (c) 2019, SAP SE, All rights reserved.
 */
package com.sap.tamagotchi.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.sap.tamagotchi.model.Owner;

@RestController
@RequestMapping("/owner")
public class OwnerController {

    @Autowired
    Owner owner;

    @GetMapping()
    public void killTamagotchi() {
        owner.killRendomDevice();
    }

}
