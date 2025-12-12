import type { IOrderController, OrderWithItems } from "./IOrderController.js";
import type { Order } from "../generated/prisma/client.js";
import type { OrderPositionCreateManyOrderInput } from "../generated/prisma/models/OrderPosition.js";
export declare class OrderController implements IOrderController {
    createOrder(userId: string, items: OrderPositionCreateManyOrderInput[]): Promise<Order>;
    deleteOrder(orderId: string): Promise<void>;
    getOrder(orderId: string): Promise<OrderWithItems | null>;
    getOrdersOfUser(userId: string): Promise<OrderWithItems[]>;
}
//# sourceMappingURL=OrderController.d.ts.map