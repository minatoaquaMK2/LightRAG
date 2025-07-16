"""
This module contains RAGAnything-specific routes for multimodal functionality.
"""

import os
import tempfile
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, Field
from ..utils_api import get_combined_auth_dependency
from ascii_colors import trace_exception

router = APIRouter(tags=["raganything"])


class MultimodalQueryRequest(BaseModel):
    query: str = Field(
        min_length=1,
        description="The query text for multimodal search",
    )
    mode: str = Field(
        default="hybrid",
        description="Query mode (local, global, hybrid, etc.)",
    )


class MultimodalQueryResponse(BaseModel):
    response: str = Field(description="The response from multimodal query")


class DocumentProcessRequest(BaseModel):
    file_path: str = Field(description="Path to the multimodal document to process")
    output_dir: str = Field(default="./output", description="Output directory for processed content")


class DocumentProcessResponse(BaseModel):
    success: bool = Field(description="Whether the document processing was successful")
    message: str = Field(description="Processing result message")
    output_path: Optional[str] = Field(description="Path to processed output", default=None)


def create_raganything_routes(rag_anything, api_key: Optional[str] = None):
    """Create RAGAnything-specific routes for multimodal functionality"""
    combined_auth = get_combined_auth_dependency(api_key)

    @router.post(
        "/multimodal/query", 
        response_model=MultimodalQueryResponse, 
        dependencies=[Depends(combined_auth)]
    )
    async def query_multimodal(request: MultimodalQueryRequest):
        """
        Handle multimodal queries using RAGAnything's query_with_multimodal method.
        
        This endpoint supports queries that can handle both text and multimodal content
        from the knowledge base.
        
        Parameters:
            request (MultimodalQueryRequest): The multimodal query request
            
        Returns:
            MultimodalQueryResponse: Response containing the multimodal query result
            
        Raises:
            HTTPException: If an error occurs during multimodal query processing
        """
        try:
            # Use RAGAnything's multimodal query method
            result = await rag_anything.query_with_multimodal(
                request.query,
                mode=request.mode
            )
            
            if isinstance(result, str):
                return MultimodalQueryResponse(response=result)
            else:
                return MultimodalQueryResponse(response=str(result))
                
        except Exception as e:
            trace_exception(e)
            raise HTTPException(status_code=500, detail=f"Multimodal query failed: {str(e)}")

    @router.post(
        "/multimodal/process-document", 
        response_model=DocumentProcessResponse, 
        dependencies=[Depends(combined_auth)]
    )
    async def process_multimodal_document(request: DocumentProcessRequest):
        """
        Process a multimodal document using RAGAnything's process_document_complete method.
        
        This endpoint can handle various document formats including PDFs, Office documents,
        images, and extract multimodal content (text, images, tables, formulas) for 
        integration into the RAG pipeline.
        
        Parameters:
            request (DocumentProcessRequest): The document processing request
            
        Returns:
            DocumentProcessResponse: Response containing processing results
            
        Raises:
            HTTPException: If an error occurs during document processing
        """
        try:
            if not os.path.exists(request.file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
            
            # Use RAGAnything's multimodal document processing
            await rag_anything.process_document_complete(
                file_path=request.file_path,
                output_dir=request.output_dir
            )
            
            return DocumentProcessResponse(
                success=True,
                message=f"Successfully processed multimodal document: {request.file_path}",
                output_path=request.output_dir
            )
            
        except Exception as e:
            trace_exception(e)
            raise HTTPException(
                status_code=500, 
                detail=f"Multimodal document processing failed: {str(e)}"
            )

    @router.post(
        "/multimodal/upload-and-process", 
        response_model=DocumentProcessResponse, 
        dependencies=[Depends(combined_auth)]
    )
    async def upload_and_process_document(
        file: UploadFile = File(..., description="Multimodal document file to upload and process"),
        output_dir: str = Form(default="./output", description="Output directory for processed content")
    ):
        """
        Upload and process a multimodal document in one step.
        
        This endpoint accepts file uploads and processes them using RAGAnything's
        multimodal capabilities.
        
        Parameters:
            file (UploadFile): The uploaded multimodal document
            output_dir (str): Output directory for processed content
            
        Returns:
            DocumentProcessResponse: Response containing processing results
            
        Raises:
            HTTPException: If an error occurs during upload or processing
        """
        temp_file_path = None
        try:
            # Create temporary file to store uploaded content
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Process the uploaded file using RAGAnything
            await rag_anything.process_document_complete(
                file_path=temp_file_path,
                output_dir=output_dir
            )
            
            return DocumentProcessResponse(
                success=True,
                message=f"Successfully uploaded and processed multimodal document: {file.filename}",
                output_path=output_dir
            )
            
        except Exception as e:
            trace_exception(e)
            raise HTTPException(
                status_code=500, 
                detail=f"Upload and processing failed: {str(e)}"
            )
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass  # Ignore cleanup errors

    return router 