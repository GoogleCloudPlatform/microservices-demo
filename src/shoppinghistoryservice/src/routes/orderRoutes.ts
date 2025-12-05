import {Router} from "express";
import type {IOrderHandler} from "../handlers/IOrderHandler.js";

export function orderRoutes(orderHandler: IOrderHandler) {
  const router = Router()

  router.post("/", orderHandler.createOrder)
  router.delete("/", orderHandler.deleteOrder)
  router.get("/", orderHandler.getOrder)
  router.get("/ofUser", orderHandler.getOrdersOfUser)

  return router;
}
