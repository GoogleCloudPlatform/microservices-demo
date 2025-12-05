import type {IOrderController} from "./IOrderController.js";
import type {Order, OrderPosition} from "../generated/prisma/client.js";
import {prisma} from "../prisma.js";


class OrderController implements IOrderController {

  async createOrder(userId: string, items: OrderPosition[]): Promise<Order> {
    return prisma.order.create({
      data: {items, userId}
    });
  }

  deleteOrder(orderId: string): Promise<void> {
    return prisma.order.delete({
      where: {id: orderId}
    });
  }

  getOrder(orderId: string): Promise<Order> {
    return prisma.order.findUnique({where: {id: orderId}, include: {orderItems: true}});
  }

  getOrdersOfUser(userId: string): Promise<Order[] | null> {
    return prisma.order.findMany({where: {userId}});
  }
}
