import {OrderController} from "./controllers/OrderController.js";
import * as grpc from "@grpc/grpc-js";
import {Server} from "@grpc/grpc-js";
import * as protoLoader from "@grpc/proto-loader";
import {ShoppingHistoryServiceImpl} from "./ShoppingHistoryServiceImpl.js";
import {fileURLToPath} from "node:url";
import * as path from "path";

const __filename = fileURLToPath(import.meta.url);

// Define the equivalent of __dirname
const __dirname = path.dirname(__filename);

// Example: Using the new __dirname to construct a path
const PROTO_PATH = path.join(__dirname, 'proto', 'shoppinghistoryservice.proto');


const packageDef = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const DEFAULT_PORT = 3000;
let PORT = DEFAULT_PORT;
const port_env = Number(process.env.PORT);
if (process.env.PORT == undefined || isNaN(port_env)) {
  console.log(`Environment variable PORT was not supplied, defaulting to ${DEFAULT_PORT}`)
} else {
  PORT = port_env;
}

const protoDescriptor = grpc.loadPackageDefinition(packageDef);
const shoppingHistoryServiceProto = protoDescriptor.shoppinghistoryservice as any;
const serviceDefinition = shoppingHistoryServiceProto.ShoppingHistoryService.service;
const server = new Server();
const controller = new OrderController();

server.addService(serviceDefinition, new ShoppingHistoryServiceImpl(controller))


server.bindAsync("0.0.0.0:"+PORT, grpc.ServerCredentials.createInsecure(), () => {});

