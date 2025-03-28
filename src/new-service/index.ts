import express, { Request, Response } from 'express';

const app = express();
const port = 3000;

app.get('/', (req: Request, res: Response) => {
  res.send('Hello from the new service!');
});

app.get('/health', (req: Request, res: Response) => {
  res.status(200).send('OK');
});

app.get('/size', (req: Request, res: Response) => {
  res.json({ size: 1024 });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});