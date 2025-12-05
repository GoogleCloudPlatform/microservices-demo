import type {IOrderController, OrderWithItems} from "./IOrderController.js";
import type {Order} from "../generated/prisma/client.js";
import {prisma} from "../prisma.js";
import type {OrderPositionCreateManyOrderInput} from "../generated/prisma/models/OrderPosition.js";


export class OrderController implements IOrderController {

  async createOrder(userId: string, items: OrderPositionCreateManyOrderInput[]): Promise<Order> {
    return prisma.order.create({
      data: {
        userId,
        orderItems: {
          createMany: {
            data: items,
            skipDuplicates: true
          },
        }
      }
    });
  }

  async deleteOrder(orderId: string): Promise<void> {
    await prisma.orderPosition.deleteMany({where: {orderId}})
    await prisma.order.delete({
      where: {id: orderId}
    });
  }

  async getOrder(orderId: string): Promise<OrderWithItems | null> {
    return prisma.order.findUnique({where: {id: orderId}, include: {orderItems: true}});
  }

  getOrdersOfUser(userId: string): Promise<OrderWithItems[]> {
    return prisma.order.findMany({where: {userId}, include: {orderItems: true}});
  }
}
