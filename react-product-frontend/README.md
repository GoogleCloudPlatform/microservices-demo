# React Product Frontend

Um frontend moderno em React + Vite que se conecta ao Product Catalog Service via gRPC.

## 🏗️ Arquitetura

```
Browser (React) → BFF (Node.js/Express) → Product Catalog Service (gRPC)
```

## 🚀 Quick Start

### Desenvolvimento Local

1. **Instalar dependências:**
```bash
npm run install:all
```

2. **Copiar o arquivo proto:**
```bash
# Certifique-se de que o arquivo demo.proto está em ../protos/demo.proto
cp ../microservices-demo/protos/demo.proto protos/
```

3. **Port-forward do Product Catalog Service:**
```bash
kubectl port-forward service/productcatalogservice 3550:3550
```

4. **Configurar variáveis de ambiente:**
```bash
# Backend
cd backend
cp env.example .env
# Edite .env se necessário

# Frontend
cd ..
echo "VITE_API_BASE_URL=http://localhost:3001/api" > .env.local
```

5. **Executar em modo desenvolvimento:**
```bash
npm run dev
```

Isso iniciará:
- Frontend React: http://localhost:3000
- Backend BFF: http://localhost:3001

### Deploy no Kubernetes

1. **Build da imagem Docker:**
```bash
docker build -t react-product-frontend:latest .
```

2. **Deploy no cluster:**
```bash
kubectl apply -f k8s-deployment.yaml
```

3. **Verificar status:**
```bash
kubectl get pods -l app=react-product-frontend
kubectl get svc react-product-frontend
```

## 📁 Estrutura do Projeto

```
react-product-frontend/
├── src/                          # Frontend React
│   ├── components/              # Componentes React
│   ├── services/               # API clients
│   ├── types/                  # TypeScript types
│   ├── utils/                  # Utilitários
│   └── main.tsx               # Entry point
├── backend/                     # Backend BFF
│   ├── src/
│   │   ├── grpc/              # gRPC clients
│   │   └── server.ts          # Express server
│   └── package.json
├── protos/                     # Protocol Buffers
│   └── demo.proto
├── k8s-deployment.yaml         # Kubernetes manifests
└── Dockerfile                 # Container image
```

## 🔌 API Endpoints

O BFF expõe os seguintes endpoints REST:

- `GET /api/products` - Lista todos os produtos
- `GET /api/products/:id` - Busca produto por ID
- `GET /api/search?q=query` - Busca produtos por texto
- `GET /health` - Health check

## 🛠️ Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev                    # Inicia frontend + backend
npm run dev:frontend          # Apenas frontend
npm run dev:backend           # Apenas backend

# Build
npm run build                 # Build completo
npm run build:frontend        # Build do frontend
npm run build:backend         # Build do backend

# Instalação
npm run install:all           # Instala deps do frontend + backend
```

## 🐳 Docker

### Build local:
```bash
docker build -t react-product-frontend .
```

### Run local:
```bash
docker run -p 3001:3001 \
  -e PRODUCT_CATALOG_SERVICE_ADDR=host.docker.internal:3550 \
  react-product-frontend
```

## 🎯 Funcionalidades

### ✅ Implementado
- ✅ Lista de produtos com grid responsivo
- ✅ Visualização detalhada de produtos
- ✅ Busca de produtos
- ✅ Design moderno e responsivo
- ✅ Estados de loading e erro
- ✅ gRPC client com retry automático
- ✅ Health checks
- ✅ Deploy no Kubernetes

### 🔮 Futuras Melhorias
- [ ] Cache de produtos
- [ ] Paginação
- [ ] Filtros por categoria
- [ ] Carrinho de compras
- [ ] Autenticação
- [ ] Métricas e observabilidade

## 🔧 Configuração

### Variáveis de Ambiente

**Backend (.env):**
```env
PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550
PORT=3001
NODE_ENV=production
```

**Frontend (.env.local):**
```env
VITE_API_BASE_URL=/api
```

### Para desenvolvimento local com port-forward:
```env
# Backend
PRODUCT_CATALOG_SERVICE_ADDR=localhost:3550

# Frontend
VITE_API_BASE_URL=http://localhost:3001/api
```

## 🚨 Troubleshooting

### Problema: "Connection refused" no gRPC
**Solução:** Verifique se o port-forward está ativo:
```bash
kubectl port-forward service/productcatalogservice 3550:3550
```

### Problema: Frontend não consegue acessar API
**Solução:** Verifique se o proxy está configurado no `vite.config.ts`:
```typescript
server: {
  proxy: {
    '/api': 'http://localhost:3001'
  }
}
```

### Problema: Imagem não carrega no Kubernetes
**Solução:** Verifique se a imagem foi enviada para o registry correto:
```bash
kubectl describe pod <pod-name>
```

## 📊 Monitoramento

### Health Checks
- Backend: `GET /health`
- Status esperado: `200 OK`

### Logs
```bash
# Logs do pod
kubectl logs -f deployment/react-product-frontend

# Logs específicos do container
kubectl logs -f deployment/react-product-frontend -c frontend
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
