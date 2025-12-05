import type {IOrderHandler} from "./IOrderHandler.js";
import type {IOrderController} from "../controllers/IOrderController.js";
import type {Request, Response} from "express";
import * as z from "zod";
import type {OrderPositionCreateManyOrderInput} from "../generated/prisma/models/OrderPosition.ts";

const OrderId = z.object({orderId: z.string()});
const UserId = z.object({userId: z.string()});
const OrderPositionCreateZod = z.object({productId: z.string(), quantity: z.number()})

export class OrderHandlerImpl implements IOrderHandler {

  constructor(private orderController: IOrderController) {
  }

  createOrder = async (req: Request, res: Response): Promise<void> => {
    let userId: string;
    let orderPositionsCreate: OrderPositionCreateManyOrderInput[];
    try {
      const payload = z.object(
        {
          userId: z.string(),
          items: z.array(OrderPositionCreateZod)
        }).parse(req.body);
      userId = payload.userId;
      orderPositionsCreate = payload.items;
    } catch (e) {
      if (e instanceof z.ZodError) {
        res.status(400);
      }
      return;
    }

    try {
      const result = await this.orderController.createOrder(userId, orderPositionsCreate);
      res.status(201).json(result);
    } catch (e) {
      res.status(400);
    }
  }

  deleteOrder = async (req: Request, res: Response): Promise<void> => {
    let orderId: string;
    try {
      orderId = OrderId.parse(req.query).orderId;
    } catch (e) {
      if (e instanceof z.ZodError) {
        res.status(400).json();
      }
      return;
    }

    try {
      if ((await this.orderController.getOrder(orderId)) == null) {
        res.status(204)
      } else {
        await this.orderController.deleteOrder(orderId);
        res.status(200);
      }
    } catch (e) {
      res.status(400);
    } finally {
      res.json();
    }
  }

  getOrdersOfUser = async (req: Request, res: Response): Promise<void> => {
    let userId: string;
    try {
      userId = UserId.parse(req.query).userId;
    } catch (e) {
      if (e instanceof z.ZodError) {
        res.status(400);
      }
      return;
    }
    try {
      const result = await this.orderController.getOrdersOfUser(userId);
      res.status(200).json(result);
    } catch (e) {
      res.status(400);
    }
  }

  getOrder = async (req: Request, res: Response): Promise<void> => {
    let orderId: string;
    try {
      orderId = OrderId.parse(req.query).orderId;
    } catch (e) {
      if (e instanceof z.ZodError) {
        res.status(400).json();
      }
      return;
    }
    try {
      const result = await this.orderController.getOrder(orderId);
      res.status(200).json(result);
    } catch (e) {
      res.status(500).json();
    }
  }
}
