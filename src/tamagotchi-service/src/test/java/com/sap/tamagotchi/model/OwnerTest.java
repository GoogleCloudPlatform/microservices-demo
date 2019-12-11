/**
 * Copyright (c) 2019, SAP SE, All rights reserved.
 */
package com.sap.tamagotchi.model;

import static java.util.Arrays.asList;
import static org.mockito.Mockito.when;
import java.util.Collection;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.junit4.SpringRunner;
import com.sap.tamagotchi.service.TamagotchiService;;

@RunWith(SpringRunner.class)
@SpringBootTest
public class OwnerTest {

    @Autowired
    Owner owner;

    @MockBean
    TamagotchiService tamagotchiService;

    Collection<Device> mockDevices;

    // @Before
    // public void init() {
    // MockitoAnnotations.initMocks(this);
    // }

    @Test
    public void testIt() {
        when(tamagotchiService.getDevices()).thenReturn(asList(new Device("elisa@sap.com", Color.BLUE)));
        owner.setData();

    }
}
