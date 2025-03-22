import uvicorn
import os
from fastapi import FastAPI, Depends
from pathlib import Path

from src.config.settings import settings
from src.user_interface.api_router import router as api_router
from src.user_interface.physical_ai_router import router as physical_ai_router
from src.user_interface.crewai_router import router as crewai_router
from src.user_interface.primavera_router import router as primavera_router
from src.user_interface.mpxj_router import mpxj_router
from src.data_ingestion.database import Database
from src.evm_engine.calculator import EVMCalculator
from src.evm_engine.physical_ai_assistant import PhysicalEVMAssistant
from src.ai_ml_analysis.analyzer import EVMAnalyzer
from src.nlg_engine.generator import NLGGenerator
from src.utils.helpers import save_sample_data, save_sample_physical_data

# Create data directory for database if it doesn't exist
db_dir = Path(settings.DATABASE_DIR)
db_dir.mkdir(parents=True, exist_ok=True)

# Create a sample data directory
sample_data_dir = Path("data/sample")
sample_data_dir.mkdir(parents=True, exist_ok=True)

# Initialize global components
db = Database()
evm_calculator = EVMCalculator()
physical_ai_assistant = PhysicalEVMAssistant(evm_calculator)
evm_analyzer = EVMAnalyzer(evm_calculator)
nlg_generator = NLGGenerator()

# Initialize FastAPI application
app = FastAPI(
    title="AI EVM Agent",
    description="Real-Time AI Agent for Earned Value Management (EVM)",
    version="1.0.0"
)

# Include API routers
app.include_router(api_router)
app.include_router(physical_ai_router)
app.include_router(crewai_router)
app.include_router(primavera_router)  # Add Primavera P6 integration router
app.include_router(mpxj_router)  # Add MPXJ file conversion router


# Dependency to get database connection
async def get_db():
    return db


# Dependency to get Physical AI Assistant
async def get_physical_ai_assistant():
    return physical_ai_assistant


# Startup event
@app.on_event("startup")
async def startup_event():
    print(f"Starting AI EVM Agent on {settings.HOST}:{settings.PORT}")
    print(f"Database initialized at {os.path.join(settings.DATABASE_DIR, settings.DATABASE_FILENAME)}")
    
    # Generate sample data files
    sample_data_path = sample_data_dir / "sample_project.json"
    if not sample_data_path.exists():
        print("Generating sample project data...")
        save_sample_data(sample_data_path)
        print(f"Sample data saved to {sample_data_path}")
    
    # Generate sample physical data
    physical_data_path = sample_data_dir / "sample_physical_data.json"
    if not physical_data_path.exists():
        print("Generating sample physical project data...")
        save_sample_physical_data(physical_data_path)
        print(f"Sample physical data saved to {physical_data_path}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down AI EVM Agent")
    if db is not None:
        db.close()


# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI EVM Agent - Real-Time Earned Value Management Assistant"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


# Physical AI capabilities info endpoint
@app.get("/physical-ai-capabilities")
async def physical_ai_capabilities():
    return {
        "message": "Physical AI for Real-World EVM Projects",
        "capabilities": [
            "Environmental impact analysis",
            "Supply chain disruption assessment",
            "On-site progress verification",
            "Resource productivity analysis",
            "Risk assessment for physical work elements",
            "IoT sensor data integration"
        ],
        "physical_endpoints": [
            "/api/v1/physical/environmental-impact",
            "/api/v1/physical/supply-chain-impact",
            "/api/v1/physical/site-progress-adjustment",
            "/api/v1/physical/at-risk-wbs-elements",
            "/api/v1/physical/resource-productivity/{project_id}",
            "/api/v1/physical/physical-vs-reported/{project_id}",
            "/api/v1/physical/environmental-scan/{project_id}"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
