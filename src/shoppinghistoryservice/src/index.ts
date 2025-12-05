import express from "express";
import {OrderController} from "./controllers/OrderController.js";
import {OrderHandlerImpl} from "./handlers/OrderHandlerImpl.ts";
import {orderRoutes} from "./routes/orderRoutes.js";

const app = express();
const PORT = 3000;

const controller = new OrderController();
const handler = new OrderHandlerImpl(controller)

app.use(express.json())
app.use("/", orderRoutes(handler));

app.get("/", (req, res) => {
  res.json({ message: "Server is running!" });
});

app.listen(PORT, () => {
  console.log(`Server started on port ${PORT}`);
});
