#!/usr/bin/env python3
"""
AI Sales quanBuy Service
Provides professional fashion advice, outfit analysis, and sales psychology
to enhance the Online Boutique shopping experience.
"""

import os
import base64
import logging
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

import grpc
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import io

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini models
gemini_vision = None
gemini_pro = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize models on startup"""
    global gemini_vision, gemini_pro
    
    # Check if we're in mock mode for local testing
    if os.getenv("MOCK_MODE", "false").lower() == "true":
        logger.info("Running in MOCK MODE - no real AI calls will be made")
        gemini_vision = "mock"
        gemini_pro = "mock"
    else:
        try:
            gemini_vision = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
            gemini_pro = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
            logger.info("Successfully initialized Gemini models")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini models: {e}")
            logger.info("Falling back to MOCK MODE")
            gemini_vision = "mock"
            gemini_pro = "mock"
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down AI quanBuy Service")

app = FastAPI(
    title="AI Sales quanBuy Service",
    description="Professional fashion advice and sales psychology for online shopping",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class StyleAnalysisRequest(BaseModel):
    image_base64: str
    user_question: str
    occasion: Optional[str] = None
    budget_range: Optional[str] = None
    user_id: Optional[str] = None

class ProductComparison(BaseModel):
    product_ids: List[str]
    user_context: str
    user_photo: Optional[str] = None

class VoiceRequest(BaseModel):
    audio_base64: Optional[str] = None
    text_input: Optional[str] = None
    image_base64: Optional[str] = None
    user_id: Optional[str] = None

class StyleRecommendation(BaseModel):
    analysis: str
    recommendations: List[Dict[str, Any]]
    persuasion_points: List[str]
    confidence_score: float
    voice_response: Optional[str] = None

class ComparisonResult(BaseModel):
    detailed_analysis: str
    winner: str
    reasoning: str
    persuasion_message: str

# Product Catalog gRPC Client
class ProductClient:
    """Client for connecting to existing Product Catalog Service"""
    
    def __init__(self):
        self.product_service_addr = os.getenv('PRODUCT_CATALOG_SERVICE_ADDR', 'productcatalogservice:3550')
        self.channel = None
        self.stub = None
        
    def connect(self):
        """Establish gRPC connection"""
        try:
            self.channel = grpc.insecure_channel(self.product_service_addr)
            # Import the generated protobuf files
            # Note: This would normally import the actual proto files
            # For now, we'll simulate the response structure
            logger.info(f"Connected to Product Catalog Service at {self.product_service_addr}")
        except Exception as e:
            logger.error(f"Failed to connect to Product Catalog Service: {e}")
            
    def get_all_products(self):
        """Get all products from catalog"""
        # Simulated product data for now - would use actual gRPC call
        return [
            {
                "id": "OLJCESPC7Z",
                "name": "Sunglasses",
                "description": "Add a modern touch to your outfits with these sleek aviator sunglasses.",
                "price": "$19.99",
                "categories": ["accessories"]
            },
            {
                "id": "1YMWWN1N4O", 
                "name": "Watch",
                "description": "This gold-tone stainless steel watch will work with most of your outfits.",
                "price": "$109.99",
                "categories": ["accessories"]
            },
            {
                "id": "66VCHSJNUP",
                "name": "Tank Top", 
                "description": "Perfectly cropped cotton tank, with a scooped neckline.",
                "price": "$18.99",
                "categories": ["clothing", "tops"]
            },
            {
                "id": "L9ECAV7KIM",
                "name": "Loafers",
                "description": "A neat addition to your summer wardrobe.",
                "price": "$89.99", 
                "categories": ["footwear"]
            }
        ]

# Initialize product client
product_client = ProductClient()

class ImageAnalyzer:
    """Gemini Vision-powered image analysis for outfit assessment"""
    
    @staticmethod
    async def analyze_outfit_photo(image_base64: str, context: str) -> Dict[str, Any]:
        """Analyze user's outfit photo with professional styling expertise"""
        
        # Mock mode for local testing
        if gemini_vision == "mock":
            return await ImageAnalyzer._mock_analyze_outfit(context)
        
        
        prompt = f"""
        You are a professional fashion quanBuy and expert sales consultant. Analyze this outfit photo with the expertise of someone who has styled celebrities and high-end clients.

        Provide a detailed analysis covering:

        1. OVERALL STYLE ASSESSMENT:
        - Style archetype (classic, modern, bohemian, edgy, romantic, etc.)
        - Current fashion relevance and trend alignment
        - Sophistication level and target demographic

        2. COLOR ANALYSIS:
        - Exact color identification with undertones
        - Skin tone compatibility (warm/cool/neutral undertones)
        - Color harmony and coordination
        - Missing color elements that would enhance the look

        3. FIT AND PROPORTIONS:
        - How well garments fit the body type
        - Proportion balance and visual weight distribution
        - Silhouette effectiveness and flattering qualities
        - Any adjustments needed for optimal fit

        4. STYLING OPPORTUNITIES:
        - What's working exceptionally well
        - Missing elements for outfit completion
        - Accessories that would elevate the look
        - Styling techniques to enhance the overall appearance

        5. OCCASION APPROPRIATENESS:
        - Suitability for the intended setting
        - Level of formality and dress code compliance
        - Confidence and impression factors

        Context: {context}

        Be encouraging yet honest, professional yet personable. Use specific fashion terminology and provide actionable styling advice. Focus on building the person's confidence while identifying genuine improvement opportunities.
        """
        
        try:
            message = HumanMessage(content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}
            ])
            
            response = gemini_vision.invoke([message])
            return {
                "analysis": response.content,
                "confidence": 0.9  # Could implement actual confidence scoring
            }
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")
    
    @staticmethod
    async def _mock_analyze_outfit(context: str) -> Dict[str, Any]:
        """Mock analysis for local testing"""
        return {
            "analysis": f"""
PROFESSIONAL STYLE ANALYSIS:

You look absolutely fantastic! Here's my expert assessment:

OVERALL STYLE: Your outfit showcases a perfect blend of classic sophistication with modern flair. The color coordination is spot-on and demonstrates excellent fashion sense.

COLOR ANALYSIS: The colors you've chosen work beautifully with your skin tone. The undertones create a harmonious palette that's both flattering and on-trend.

FIT & PROPORTIONS: Everything fits you perfectly! The proportions are well-balanced and create a very flattering silhouette that accentuates your best features.

STYLING OPPORTUNITIES: You've already nailed the basics! To take this look to the next level, I'd suggest adding one statement accessory that will make this outfit truly unforgettable.

CONFIDENCE FACTOR: You should feel absolutely confident in this look - it's polished, appropriate, and shows your personal style beautifully.

Context: {context}
            """,
            "confidence": 0.95
        }

class StyleEngine:
    """Advanced style recommendation engine with sales psychology"""
    
    @staticmethod
    async def generate_recommendations(
        image_analysis: str, 
        available_products: List[Dict], 
        user_context: str
    ) -> StyleRecommendation:
        """Generate personalized style recommendations with persuasive sales messaging"""
        
        # Mock mode for local testing
        if gemini_pro == "mock":
            return await StyleEngine._mock_generate_recommendations(available_products, user_context)
        
        # Convert products to detailed text for LLM
        products_text = "\n".join([
            f"- {p['name']} ({p['price']}): {p['description']} | Categories: {', '.join(p['categories'])}"
            for p in available_products
        ])
        
        prompt = f"""
        You are an elite personal quanBuy and master sales consultant. Your clients include celebrities, executives, and fashion-forward individuals who trust your expertise implicitly.

        CONTEXT:
        Image Analysis: {image_analysis}
        User Context: {user_context}

        AVAILABLE PRODUCTS:
        {products_text}

        Your task is to provide exceptional styling recommendations that:

        1. DEMONSTRATE EXPERTISE through specific fashion knowledge
        2. BUILD CONFIDENCE with genuine, well-reasoned compliments  
        3. CREATE DESIRE through vivid outcome visualization
        4. DRIVE ACTION with compelling, time-sensitive messaging

        Provide your response in this structure:

        EXPERT ASSESSMENT:
        [Professional analysis of their current look with specific fashion terminology]

        STYLING RECOMMENDATIONS:
        [Specific product suggestions with detailed reasoning about why each piece works]

        CONFIDENCE BUILDING:
        [Genuine compliments about what they're doing right, building on their strengths]

        OUTCOME VISUALIZATION:
        [Paint a picture of how they'll look and feel with your recommendations]

        COMPELLING CALL TO ACTION:
        [Create urgency and desire to purchase, using psychological principles]

        Be authentic, enthusiastic, and genuinely helpful while subtly applying proven sales psychology. Remember: you're not just selling products, you're selling confidence, transformation, and a better version of themselves.
        """
        
        try:
            response = gemini_pro.invoke(prompt)
            
            # Extract specific recommendations (simplified for demo)
            recommended_products = []
            for product in available_products[:3]:  # Top 3 recommendations
                recommended_products.append({
                    "id": product["id"],
                    "name": product["name"],
                    "price": product["price"],
                    "reason": f"Perfect complement to your style and {user_context}"
                })
            
            return StyleRecommendation(
                analysis=response.content,
                recommendations=recommended_products,
                persuasion_points=[
                    "Investment in your confidence",
                    "Immediate style transformation",
                    "Professional image enhancement"
                ],
                confidence_score=0.92,
                voice_response="You're going to love how you look and feel in this!"
            )
        except Exception as e:
            logger.error(f"Style recommendation generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
    
    @staticmethod
    async def _mock_generate_recommendations(available_products: List[Dict], user_context: str) -> StyleRecommendation:
        """Mock recommendations for local testing"""
        
        # Pick top 3 products for demo
        recommended_products = []
        for i, product in enumerate(available_products[:3]):
            recommended_products.append({
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "reason": f"Perfect complement to your style! This {product['name']} will elevate your entire look and give you that confidence boost you deserve."
            })
        
        mock_analysis = f"""
EXPERT STYLING RECOMMENDATIONS:

Based on your photo and question "{user_context}", here's what I recommend:

🎯 STYLE ASSESSMENT: Your natural sense of style is evident! You have excellent instincts and just need a few key pieces to take your look from great to absolutely stunning.

✨ MY TOP RECOMMENDATIONS:
{chr(10).join([f"• {p['name']} - {p['reason']}" for p in recommended_products])}

💫 CONFIDENCE BUILDING: You have incredible potential! These pieces will help you feel as amazing as you look. Trust your instincts - you're on the right track.

🛍️ STYLING TIP: The key is confidence! These accessories will give you that extra boost of sophistication that makes all the difference.

🎉 TRANSFORMATION PROMISE: With these additions, you'll walk into any room feeling like the best-dressed person there!
        """
        
        return StyleRecommendation(
            analysis=mock_analysis,
            recommendations=recommended_products,
            persuasion_points=[
                "Investment in your confidence and professional image",
                "Instant style transformation with minimal effort", 
                "Perfect for your personal style and lifestyle needs"
            ],
            confidence_score=0.92,
            voice_response="You're going to look absolutely amazing! These pieces are perfect for you!"
        )

class ComparisonEngine:
    """Product comparison with detailed analysis and persuasive recommendations"""
    
    @staticmethod
    async def compare_products(product_ids: List[str], user_context: str, user_photo: str = None) -> ComparisonResult:
        """Generate detailed product comparisons with sales psychology"""
        
        # Get products from catalog
        all_products = product_client.get_all_products()
        products_to_compare = [p for p in all_products if p["id"] in product_ids]
        
        if len(products_to_compare) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 products to compare")
        
        products_text = "\n".join([
            f"PRODUCT: {p['name']} - {p['price']}\n"
            f"Description: {p['description']}\n"
            f"Categories: {', '.join(p['categories'])}\n"
            for p in products_to_compare
        ])
        
        photo_context = ""
        if user_photo:
            photo_context = "I can see your current outfit in the photo you shared. "
        
        prompt = f"""
        You are a master quanBuy and sales expert conducting a detailed product comparison for a valued client.

        {photo_context}PRODUCTS TO COMPARE:
        {products_text}

        USER CONTEXT: {user_context}

        Provide a comprehensive comparison that includes:

        1. DETAILED FEATURE ANALYSIS
        - Quality indicators and construction details
        - Style versatility and trend relevance
        - Value proposition and price justification

        2. SUITABILITY ASSESSMENT  
        - Which product better serves the user's specific needs
        - Occasion appropriateness and styling potential
        - Long-term wardrobe value

        3. EXPERT RECOMMENDATION
        - Clear winner with detailed reasoning
        - Specific benefits the chosen product provides
        - Why this choice will enhance their style and confidence

        4. PERSUASIVE CLOSING
        - Emotional benefits and transformation promise
        - Urgency or scarcity elements if appropriate
        - Confidence-building reassurance about the choice

        Be decisive, authoritative, and genuinely helpful. Your expertise should shine through while building excitement about the recommended choice.
        """
        
        try:
            response = gemini_pro.invoke(prompt)
            
            # For demo, declare first product as winner
            winner = products_to_compare[0]
            
            return ComparisonResult(
                detailed_analysis=response.content,
                winner=winner["name"],
                reasoning=f"Superior quality and style alignment for your needs",
                persuasion_message=f"The {winner['name']} is the clear choice - you'll love how it elevates your entire look!"
            )
        except Exception as e:
            logger.error(f"Product comparison failed: {e}")
            raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

# Initialize service components
image_analyzer = ImageAnalyzer()
style_engine = StyleEngine()
comparison_engine = ComparisonEngine()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-sales-quanBuy",
        "version": "1.0.0",
        "models_initialized": gemini_vision is not None and gemini_pro is not None
    }

@app.post("/analyze-style", response_model=StyleRecommendation)
async def analyze_style(request: StyleAnalysisRequest):
    """Main endpoint for outfit analysis and style recommendations"""
    
    try:
        logger.info(f"Style analysis request from user: {request.user_id}")
        
        # 1. Analyze uploaded image
        context = f"Question: {request.user_question}"
        if request.occasion:
            context += f", Occasion: {request.occasion}"
        if request.budget_range:
            context += f", Budget: {request.budget_range}"
            
        image_analysis = await image_analyzer.analyze_outfit_photo(
            request.image_base64, 
            context
        )
        
        # 2. Get available products
        available_products = product_client.get_all_products()
        
        # 3. Generate personalized recommendations
        recommendations = await style_engine.generate_recommendations(
            image_analysis["analysis"],
            available_products,
            request.user_question
        )
        
        logger.info(f"Successfully generated recommendations for user: {request.user_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Style analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/compare-products", response_model=ComparisonResult)
async def compare_products(request: ProductComparison):
    """Compare specific products with detailed analysis"""
    
    try:
        logger.info(f"Product comparison request: {request.product_ids}")
        
        comparison = await comparison_engine.compare_products(
            request.product_ids,
            request.user_context,
            request.user_photo
        )
        
        logger.info(f"Successfully compared products: {request.product_ids}")
        return comparison
        
    except Exception as e:
        logger.error(f"Product comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.post("/voice-quanBuy")
async def voice_quanBuy(request: VoiceRequest):
    """Voice-activated styling assistant (placeholder for voice integration)"""
    
    try:
        # For now, handle text input - voice integration would be added here
        text_input = request.text_input or "How do I look?"
        
        if request.image_base64:
            # Process image with voice context
            style_request = StyleAnalysisRequest(
                image_base64=request.image_base64,
                user_question=text_input,
                user_id=request.user_id
            )
            
            result = await analyze_style(style_request)
            
            return {
                "text_response": result.analysis,
                "voice_response": result.voice_response,
                "recommendations": result.recommendations
            }
        else:
            # Voice-only interaction
            return {
                "text_response": "I'd love to help! Please take a photo so I can see your outfit.",
                "voice_response": "I'd love to help! Please take a photo so I can see your outfit and give you expert styling advice."
            }
            
    except Exception as e:
        logger.error(f"Voice quanBuy interaction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Voice interaction failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "AI Sales quanBuy",
        "version": "1.0.0",
        "description": "Professional fashion advice and sales psychology for online shopping",
        "endpoints": [
            "/analyze-style",
            "/compare-products", 
            "/voice-quanBuy",
            "/health"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # Connect to product catalog on startup
    product_client.connect()
    
    # Run the service
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)