import type {IOrderController, OrderWithItems} from "./IOrderController.js";
import {prisma} from "../prisma.js";
import {Prisma} from "@prisma/client";


export class OrderController implements IOrderController {

  async createOrder(userId: string, items: Prisma.OrderPositionCreateManyOrderInput[]): Promise<OrderWithItems> {
    return prisma.order.create({
      data: {
        userId,
        orderItems: {
          createMany: {
            data: items,
            skipDuplicates: true
          },
        }
      },
      include: {
        orderItems: true
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
