import type {IOrderHandler} from "./IOrderHandler.js";
import type {IOrderController} from "../controllers/IOrderController.js";
import type {Request, Response} from "express";
import * as z from "zod";

const OrderId = z.object({orderId: z.string()});
const UserId = z.object({userId: z.string()});


export class OrderHandlerImpl implements IOrderHandler {

  constructor(private orderController: IOrderController) {
  }

  createOrder = async (req: Request, res: Response): Promise<void> => {
    const {userId} = req.body;
    const items = req.body!.items;

    try {
      const result = await this.orderController.createOrder(userId, items);
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
        res.status(400);
      }
      return;
    }

    try {
      await this.orderController.deleteOrder(orderId);
      res.status(200);
    } catch (e) {
      res.status(400);
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
      res.status(201).json(result);
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
        res.status(400);
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
