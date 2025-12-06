import {type Order, type OrderPosition, Prisma} from "@prisma/client";

export type OrderWithItems = Order & { orderItems: OrderPosition[];}

export interface IOrderController {
  createOrder(userId: string, items: Prisma.OrderPositionCreateManyOrderInput[]): Promise<Order>

  getOrdersOfUser(userId: string): Promise<OrderWithItems[]>;

  getOrder(orderId: string): Promise<OrderWithItems | null>

  deleteOrder(orderId: string): Promise<void>;

}
