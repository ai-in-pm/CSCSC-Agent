# MPXJ Router for CSCSC AI Agent
# This module provides API endpoints for file format conversions and project data analysis

import os
import tempfile
import shutil
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

# Import the MPXJ wrapper
from src.integration.mpxj_wrapper import MPXJConverter, HAS_MPXJ

# Define the router
mpxj_router = APIRouter(
    prefix="/api/v1/mpxj",
    tags=["mpxj"],
    responses={404: {"description": "Not found"}},
)

# Define models for request and response data
class FormatInfo(BaseModel):
    extension: str
    description: str

class FileInfo(BaseModel):
    name: str
    size: int
    format: str

class ProjectStatistics(BaseModel):
    name: Optional[str] = None
    task_count: int = 0
    normal_task_count: int = 0
    milestone_count: int = 0
    summary_task_count: int = 0
    resource_count: int = 0
    total_duration_days: float = 0
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    status_date: Optional[datetime] = None
    critical_path_length: int = 0

class ConversionRequest(BaseModel):
    output_format: str = Field(..., description="File extension for the output format (e.g., '.xml', '.mpx')")    

class DataExtractionRequest(BaseModel):
    extract_critical_path: bool = Field(False, description="Extract tasks on the critical path")
    extract_statistics: bool = Field(True, description="Extract project statistics")
    extract_tables: List[str] = Field([], description="Tables to extract (tasks, resources, assignments, relationships, calendars)")

# Global upload directory
UPLOAD_DIR = Path(tempfile.gettempdir()) / "cscsc_mpxj_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)

# Initialize MPXJ converter if available
mpxj_converter = MPXJConverter() if HAS_MPXJ else None

# Helper functions
def get_mpxj_converter():
    """Get the MPXJ converter instance, raising an exception if not available"""
    if not HAS_MPXJ:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="MPXJ library is not available. Please install it with 'pip install mpxj'"
        )
    return mpxj_converter

@mpxj_router.get("/formats", response_model=Dict[str, List[FormatInfo]])
async def get_supported_formats():
    """Get supported file formats for MPXJ"""
    converter = get_mpxj_converter()
    
    read_formats = [
        FormatInfo(extension=ext, description=desc)
        for ext, desc in converter.SUPPORTED_READ_FORMATS.items()
    ]
    
    write_formats = [
        FormatInfo(extension=ext, description=desc)
        for ext, desc in converter.SUPPORTED_WRITE_FORMATS.items()
    ]
    
    return {
        "read_formats": read_formats,
        "write_formats": write_formats
    }

@mpxj_router.post("/upload", response_model=FileInfo)
async def upload_project_file(file: UploadFile = File(...)):
    """Upload a project file for processing"""
    converter = get_mpxj_converter()
    
    # Generate a unique filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    # Save the uploaded file
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        file.file.close()
    
    # Verify file format
    if not converter.is_readable(str(file_path)):
        # Clean up the file
        os.unlink(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format"
        )
    
    # Get file size and format
    file_size = file_path.stat().st_size
    file_format = converter.detect_file_format(str(file_path))
    
    return FileInfo(
        name=filename,
        size=file_size,
        format=file_format
    )

@mpxj_router.post("/convert/{filename}")
async def convert_project_file(filename: str, conversion: ConversionRequest):
    """Convert a project file to another format"""
    converter = get_mpxj_converter()
    
    # Check if the file exists
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if the output format is supported
    if not converter.is_writable(f"test{conversion.output_format}"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported output format: {conversion.output_format}"
        )
    
    # Generate output filename
    output_filename = f"{file_path.stem}{conversion.output_format}"
    output_path = UPLOAD_DIR / output_filename
    
    try:
        # Convert the file
        converter.convert_file(str(file_path), str(output_path))
        
        # Return the converted file
        return FileResponse(
            path=output_path,
            filename=output_filename,
            media_type="application/octet-stream"
        )
    except Exception as e:
        logger.error(f"Error converting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting file: {str(e)}"
        )

@mpxj_router.post("/analyze/{filename}")
async def analyze_project_file(filename: str, extraction: DataExtractionRequest):
    """Analyze a project file and extract data"""
    converter = get_mpxj_converter()
    
    # Check if the file exists
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Read the project file
        project = converter.read_project(str(file_path))
        
        # Initialize response data
        response_data = {}
        
        # Extract project statistics if requested
        if extraction.extract_statistics:
            stats = converter.get_project_statistics(project)
            response_data["statistics"] = stats
        
        # Extract critical path if requested
        if extraction.extract_critical_path:
            critical_path = converter.extract_critical_path(project)
            response_data["critical_path"] = [
                {
                    "id": task.getID(),
                    "name": task.getName(),
                    "start": task.getStart().isoformat() if task.getStart() else None,
                    "finish": task.getFinish().isoformat() if task.getFinish() else None,
                    "duration": task.getDuration().getDuration() if task.getDuration() else None,
                    "duration_units": str(task.getDuration().getUnits()) if task.getDuration() else None,
                }
                for task in critical_path
            ]
        
        # Extract tables if requested
        if extraction.extract_tables:
            # Get all data as dataframes
            dataframes = converter.project_to_dataframes(project)
            
            # Extract requested tables
            tables = {}
            for table_name in extraction.extract_tables:
                if table_name in dataframes:
                    # Convert dataframe to records (list of dicts)
                    tables[table_name] = dataframes[table_name].to_dict(orient="records")
            
            response_data["tables"] = tables
        
        return JSONResponse(content=response_data)
    except Exception as e:
        logger.error(f"Error analyzing file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing file: {str(e)}"
        )

@mpxj_router.post("/import-to-database/{filename}")
async def import_to_database(filename: str):
    """Import a project file to the SQLite database"""
    converter = get_mpxj_converter()
    
    # Check if the file exists
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Define database path
        db_path = str(Path("data") / "mpxj_projects.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Import to database
        converter.import_to_database(str(file_path), db_path)
        
        return JSONResponse(content={
            "status": "success",
            "message": f"Project imported to database: {db_path}",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error importing to database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing to database: {str(e)}"
        )

@mpxj_router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a previously uploaded file"""
    # Check if the file exists
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    try:
        # Delete the file
        os.unlink(file_path)
        
        return JSONResponse(content={
            "status": "success",
            "message": f"File deleted: {filename}"
        })
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )
