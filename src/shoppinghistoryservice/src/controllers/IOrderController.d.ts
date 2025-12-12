import type { Order, OrderPosition } from "../generated/prisma/client.js";
import type { OrderPositionCreateManyOrderInput } from "../generated/prisma/models/OrderPosition.ts";
export type OrderWithItems = Order & {
    orderItems: OrderPosition[];
};
export interface IOrderController {
    createOrder(userId: string, items: OrderPositionCreateManyOrderInput[]): Promise<Order>;
    getOrdersOfUser(userId: string): Promise<OrderWithItems[]>;
    getOrder(orderId: string): Promise<OrderWithItems | null>;
    deleteOrder(orderId: string): Promise<void>;
}
//# sourceMappingURL=IOrderController.d.ts.map