import type {Order, OrderPosition} from "../generated/prisma/client.js";

export interface IOrderController {
  createOrder(userId: string, items: OrderPosition[]): Promise<Order>

  getOrdersOfUser(userId: string): Promise<Order[] | null>;

  getOrder(orderId: string): Promise<Order>

  deleteOrder(orderId: string): Promise<void>;

}
