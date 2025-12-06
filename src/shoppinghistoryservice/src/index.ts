import express from "express";
import {OrderController} from "./controllers/OrderController.js";
import {OrderHandlerImpl} from "./handlers/OrderHandlerImpl.js";
import {orderRoutes} from "./routes/orderRoutes.js";

const app = express();
const DEFAULT_PORT = 3000;
let PORT = DEFAULT_PORT;
const port_env = Number(process.env.PORT);
if (process.env.PORT == undefined || isNaN(port_env)) {
  console.log(`Environment variable PORT was not supplied, defaulting to ${DEFAULT_PORT}`)
} else {
  PORT = port_env;
}

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
