import type {Request, Response} from "express";

export interface IOrderHandler {
  createOrder(req: Request, res: Response): Promise<void>

  getOrdersOfUser(req: Request, res: Response): Promise<void>;

  getOrder(req: Request, res: Response): Promise<void>

  deleteOrder(req: Request, res: Response): Promise<void>;

}
