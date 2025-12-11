import {type handleUnaryCall, type UntypedHandleCall} from "@grpc/grpc-js";
import type {IOrderController} from "./controllers/IOrderController.js";
import type {DeleteOrderRequest, Empty, GetOrderRequest} from "./generated/shoppinghistoryservice.js";
import {CreateOrderRequest, GetOrdersOfUserRequest, Order, Orders,} from "./generated/shoppinghistoryservice.js"
import {Prisma} from "@prisma/client";
import {Status} from "@grpc/grpc-js/build/src/constants.js";

export class ShoppingHistoryServiceImpl {

  [name: string]: UntypedHandleCall | any;

  constructor(private controller: IOrderController) {
  }

  CreateOrder: handleUnaryCall<CreateOrderRequest, Order> = (call, callback) => {
    const positionsPrisma: Prisma.OrderPositionCreateManyOrderInput[] = call.request.positions.map(pos => {
      return {productId: pos.product_id, quantity: pos.quantity}
    });
    this.controller.createOrder(call.request.user_id, positionsPrisma).then(order => {
      callback(null, {
        created_at: order.placedOn,
        order_id: order.id,
        order_items: order.orderItems.map(item => {
          return {product_id: item.productId, quantity: item.quantity}
        }),
        user_id: order.userId
      });
    })
      .catch(_ => {
        callback({
          code: Status.INTERNAL,
          details: "Internal Server error"
        }, null)
      })
  }

  GetOrder: handleUnaryCall<GetOrderRequest, Order> = (call, callback) => {
    this.controller.getOrder(call.request.order_id)
      .then(order => {
        if (order == null) {
          return callback({
            code: Status.NOT_FOUND,
            details: `Order with ID ${call.request.order_id} not found`
          }, null)
        }
        const payload = {
          created_at: order.placedOn,
          order_id: order.id,
          order_items: order.orderItems.map(item => {
            return {product_id: item.productId, quantity: item.quantity}
          }),
          user_id: order.userId
        };
        callback(null, payload);
      })
      .catch(_ => {
        callback({
          code: Status.INTERNAL,
          details: "Internal Server error"
        }, null)
      })
  }

  GetOrdersOfUser: handleUnaryCall<GetOrdersOfUserRequest, Orders> = (call, callback) => {
    this.controller.getOrdersOfUser(call.request.user_id)
      .then(orders => {
        callback(null, {
          orders:
            orders.map(order => {
              return {
                created_at: order.placedOn, order_id: order.id, order_items: order.orderItems.map(item => {
                  return {product_id: item.productId, quantity: item.quantity}
                }), user_id: order.userId
              }
            })
        });
      })
      .catch(_ => {
        callback({
          code: Status.INTERNAL,
          details: "Internal Server error"
        }, null)
      });
  }

  DeleteOrder: handleUnaryCall<DeleteOrderRequest, Empty> = (call, callback) => {
    this.controller.deleteOrder(call.request.order_id).then(() => {
      callback(null, {})
    })
      .catch(_ => {
        callback({
          code: Status.INTERNAL,
          details: "Internal Server error"
        }, null)
      });
  }
}
