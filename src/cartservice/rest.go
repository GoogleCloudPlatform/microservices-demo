// Copyright 2022 Skyramp, Inc.
//
//	Licensed under the Apache License, Version 2.0 (the "License");
//	you may not use this file except in compliance with the License.
//	You may obtain a copy of the License at
//
//	http://www.apache.org/licenses/LICENSE-2.0
//
//	Unless required by applicable law or agreed to in writing, software
//	distributed under the License is distributed on an "AS IS" BASIS,
//	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//	See the License for the specific language governing permissions and
//	limitations under the License.
package main

import (
	pb "cartservice/genproto"
	"fmt"

	"github.com/gin-gonic/gin"
)

func get(c *gin.Context) {
	user_id := c.Param("user_id")
	cart := GetCart(user_id)
	if cart != nil {
		c.JSON(200, cart)
	} else {
		c.JSON(404, gin.H{"error": fmt.Sprintf("cart not found for user_id [%s]", user_id)})
	}
}

func post(c *gin.Context) {
	user_id := c.Param("user_id")
	if len(user_id) < 1 {
		c.JSON(403, gin.H{"error": fmt.Sprintf("invalid user id [%s]", user_id)})
		return
	}
	var item pb.CartItem
	if err := c.ShouldBindJSON(&item); err != nil {
		c.JSON(501, gin.H{"error": "failed updating cart"})
		return
	}
	AddItem(user_id, item.ProductId, item.Quantity)
	c.JSON(200, gin.H{"success": "200 OK"})
}

func delete(c *gin.Context) {
	user_id := c.Param("user_id")
	if len(user_id) < 1 {
		c.JSON(403, gin.H{"error": fmt.Sprintf("invalid user id [%s]", user_id)})
		return
	}
	EmtyCart(user_id)
	c.JSON(200, gin.H{"success": "200 OK"})
}

func runRest(port string) {
	go func() {
		log.Infof("rest server started on port %s", port)
		router := gin.Default()
		router.GET("/cart/user_id/:user_id", get)
		router.POST("/cart/user_id/:user_id", post)
		router.DELETE("/cart/user_id/:user_id", delete)
		router.Run(fmt.Sprintf("0.0.0.0:%s", port))
	}()
}
