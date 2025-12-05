import type {Order, OrderPosition} from "../generated/prisma/client.js";

export type OrderWithItems = Order & { orderItems: OrderPosition[];}

export interface IOrderController {
  createOrder(userId: string, items: OrderPosition[]): Promise<Order>

  getOrdersOfUser(userId: string): Promise<OrderWithItems[]>;

  getOrder(orderId: string): Promise<OrderWithItems | null>

  deleteOrder(orderId: string): Promise<void>;

}
