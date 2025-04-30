from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from psycopg2.extras import RealDictCursor
from repository.database import get_db_connection
from service.wave import waves
from fastapi import HTTPException, status

router = APIRouter(prefix='/wave', tags=['wave'])

@router.post("/process_waves/")
async def process_waves(data: Dict[str, Any]):
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request body cannot be empty"
        )
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        result = waves(data, cursor, conn)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))