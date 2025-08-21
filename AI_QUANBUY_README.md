# AI Personal quanBuy Microservice

An intelligent fashion advisor that provides professional outfit recommendations and personalized emotional feedback to encourage purchasing decisions. Built as an extension to Google's Online Boutique microservices demo.

## 🎯 Overview

The AI Personal quanBuy transforms the online shopping experience by acting as a virtual sales consultant. It analyzes customer photos, provides expert styling advice, and uses proven sales psychology to encourage confident purchasing decisions - perfect for fitting room scenarios where typing is inconvenient.

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                     │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Service (Go)                                         │
│  ├─ AI quanBuy UI (HTML/JS)                                    │
│  │  ├─ Photo Upload (Drag & Drop)                              │
│  │  ├─ Voice Recognition (Web Speech API)                      │
│  │  ├─ Real-time Styling Interface                             │
│  │  └─ Responsive Mobile Design                                │
│  └─ HTTP Proxy Layer                                           │
│     ├─ /ai-quanBuy → UI Page                                   │
│     ├─ /api/analyze-style → AI Service                         │
│     ├─ /api/compare-products → AI Service                      │
│     └─ /api/voice-quanBuy → AI Service                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI quanBuy Service (Python/FastAPI)         │
├─────────────────────────────────────────────────────────────────┤
│  Core Components:                                               │
│  ├─ ImageAnalyzer (Gemini Vision)                              │
│  │  ├─ Outfit Photo Analysis                                   │
│  │  ├─ Color & Style Assessment                                │
│  │  ├─ Fit & Proportions Analysis                              │
│  │  └─ Professional Fashion Expertise                          │
│  │                                                             │
│  ├─ StyleEngine (Gemini Pro)                                   │
│  │  ├─ Personalized Recommendations                            │
│  │  ├─ Sales Psychology Integration                            │
│  │  ├─ Confidence Building Messaging                           │
│  │  └─ Persuasive Call-to-Actions                             │
│  │                                                             │
│  ├─ ComparisonEngine                                           │
│  │  ├─ Product Feature Analysis                                │
│  │  ├─ Suitability Assessment                                  │
│  │  └─ Expert Recommendations                                  │
│  │                                                             │
│  └─ ProductClient (gRPC)                                       │
│     └─ Integration with Product Catalog                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Google AI Platform Integration                      │
├─────────────────────────────────────────────────────────────────┤
│  ├─ Gemini 1.5 Flash (Vision)                                  │
│  │  └─ Real-time outfit photo analysis                         │
│  └─ Gemini 1.5 Pro (Analysis)                                  │
│     └─ Advanced styling recommendations                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Existing Microservices                         │
├─────────────────────────────────────────────────────────────────┤
│  └─ Product Catalog Service (gRPC)                             │
│     ├─ Product Information                                      │
│     ├─ Pricing Data                                            │
│     └─ Category Classification                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Google Kubernetes Engine                     │
├─────────────────────────────────────────────────────────────────┤
│  Kubernetes Pods:                                              │
│  ├─ aiquanBuyservice                                           │
│  │  ├─ Port: 8080                                              │
│  │  ├─ Environment: MOCK_MODE=true (local)                     │
│  │  ├─ Resources: 200m CPU, 180Mi RAM                          │
│  │  └─ Health Checks: /health endpoint                         │
│  │                                                             │
│  ├─ frontend                                                   │
│  │  ├─ Port: 8080                                              │
│  │  ├─ Environment: AI_QUANBUY_SERVICE_ADDR                    │
│  │  └─ Load Balancer: External access                          │
│  │                                                             │
│  └─ productcatalogservice                                      │
│     ├─ Port: 3550 (gRPC)                                       │
│     └─ Product data integration                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 Design Philosophy

### Voice-First Experience
- **Hands-free interaction**: Perfect for fitting rooms where typing is inconvenient
- **Web Speech API**: Native browser voice recognition
- **Conversational interface**: Natural language interaction with the AI quanBuy

### Professional Fashion Expertise
- **Celebrity quanBuy knowledge**: Trained on high-end fashion expertise
- **Technical fashion analysis**: Color theory, fit assessment, style archetypes
- **Trend awareness**: Current fashion relevance and style recommendations

### Sales Psychology Integration
- **Confidence building**: Genuine compliments based on visual analysis
- **Outcome visualization**: Paint pictures of transformation and success
- **Persuasive messaging**: Proven sales techniques without being pushy
- **Urgency creation**: Time-sensitive recommendations when appropriate

## 🚀 Key Features

### 1. Intelligent Photo Analysis
```python
# Core analysis capabilities
- Style archetype identification (classic, modern, bohemian, etc.)
- Color analysis with undertone matching
- Fit and proportion assessment
- Occasion appropriateness evaluation
- Professional styling opportunities
```

### 2. Personalized Recommendations
```python
# Recommendation engine features
- Product matching from existing catalog
- Style enhancement suggestions
- Confidence-building messaging
- Persuasive call-to-actions
- Voice response generation
```

### 3. Voice Integration
```javascript
// Web Speech API integration
- Real-time voice recognition
- Natural language processing
- Hands-free photo upload
- Voice response playback
- Mobile-optimized interface
```

### 4. Product Comparison
```python
# Advanced comparison features
- Feature-by-feature analysis
- Quality and value assessment
- Style versatility evaluation
- Expert recommendations with reasoning
```

## 🛠️ Technical Implementation

### Backend Service (Python/FastAPI)
- **Framework**: FastAPI for high-performance async API
- **AI Models**: Google Gemini 1.5 Flash (Vision) + Pro (Analysis)
- **Architecture**: Modular components with clear separation of concerns
- **Mock Mode**: Local testing without API keys
- **Health Checks**: Kubernetes-ready health monitoring

### Frontend Integration (Go)
- **Pattern**: HTTP proxy for seamless integration
- **Routing**: Dedicated AI quanBuy routes
- **Templates**: Server-side rendered UI with JavaScript enhancement
- **Responsive**: Mobile-first design for fitting room use

### Kubernetes Deployment
- **Scalability**: Horizontal pod autoscaling ready
- **Security**: Non-root containers with security contexts
- **Observability**: Health checks and logging integration
- **Environment**: Configurable for local/cloud deployment

## 🔧 Configuration

### Environment Variables
```bash
# AI quanBuy Service
MOCK_MODE=true                    # Enable mock mode for local testing
GOOGLE_API_KEY=your_api_key      # Google AI API key (production)
PRODUCT_CATALOG_SERVICE_ADDR=productcatalogservice:3550

# Frontend Service  
AI_QUANBUY_SERVICE_ADDR=aiquanBuyservice:80
```

### Resource Requirements
```yaml
# Production recommendations
aiquanBuyservice:
  requests:
    cpu: 200m
    memory: 180Mi
  limits:
    cpu: 300m
    memory: 300Mi
```

## 📱 User Experience Flow

1. **Photo Upload**: User takes/uploads outfit photo via drag-drop interface
2. **Voice Input**: Optional voice question about their look or styling needs
3. **AI Analysis**: Gemini Vision analyzes photo with professional expertise
4. **Style Recommendations**: AI generates personalized product suggestions
5. **Confidence Building**: Encouraging feedback with specific compliments
6. **Purchase Encouragement**: Persuasive messaging to drive buying decisions

## 🔐 Security Considerations

- **Image Processing**: Photos processed securely through Google AI
- **API Keys**: Secured via Kubernetes secrets
- **Container Security**: Non-privileged containers with security contexts
- **Network Policies**: Microservice-to-microservice communication controls

## 🚀 Deployment Guide

### Local Development (Minikube)
```bash
# Build and deploy
eval $(minikube docker-env)
docker build -t aiquanBuyservice:latest ./src/aistylistservice
kubectl apply -f kubernetes-manifests/aistylistservice.yaml

# Access the service
kubectl port-forward svc/frontend 8080:80
open http://localhost:8080/ai-quanBuy
```

### Production (GKE)
```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/aiquanBuyservice ./src/aistylistservice

# Deploy with real API keys
kubectl create secret generic google-api-key --from-literal=api-key=YOUR_KEY
kubectl apply -f kubernetes-manifests/
```

## 🎯 Business Impact

- **Increased Conversion**: Professional styling advice reduces purchase hesitation
- **Enhanced UX**: Voice-first interface perfect for mobile/fitting room use
- **Personalization**: AI-driven recommendations increase customer satisfaction
- **Sales Psychology**: Proven techniques to encourage confident purchasing decisions

## 📈 Future Enhancements

- **Multi-language Support**: International market expansion
- **Style Memory**: Remember user preferences across sessions
- **Outfit Coordination**: Complete look recommendations across categories
- **Social Integration**: Share styling success stories
- **Analytics Dashboard**: Track styling effectiveness and conversion rates

## 🎨 quanBuy Name Origin

The name "quanBuy" represents the quantitative approach to buying decisions - combining data-driven fashion analysis with psychology-based purchase encouragement. It embodies the AI's ability to quantify style elements and guide users toward confident buying choices.

---

*Built with ❤️ using Google Cloud AI, Kubernetes, and modern web technologies*