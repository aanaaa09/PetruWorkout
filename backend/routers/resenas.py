from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..config.database import get_db
from ..models.resena import Resena

router = APIRouter(prefix="/api/resenas", tags=["resenas"])


@router.get("/publicas")
def obtener_resenas_publicas(
        limit: int = 10,
        db: Session = Depends(get_db)
):
    """
    Obtiene las reseñas aprobadas y visibles para mostrar en la landing page.
    Solo devuelve reseñas que hayan sido aprobadas por el admin.
    """
    try:
        resenas = db.query(Resena).filter(
            Resena.aprobada == True,
            Resena.visible == True
        ).order_by(Resena.fecha_creacion.desc()).limit(limit).all()

        return {
            'success': True,
            'total': len(resenas),
            'resenas': [
                {
                    'id': r.id,
                    'nombre': r.nombre_autor,
                    'texto': r.texto,
                    'valoracion': r.valoracion,
                    'fecha': r.fecha_creacion.isoformat() if r.fecha_creacion else None
                }
                for r in resenas
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estadisticas")
def obtener_estadisticas_resenas(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas de las reseñas (promedio, total, etc.)
    """
    try:
        resenas = db.query(Resena).filter(
            Resena.aprobada == True,
            Resena.visible == True
        ).all()

        if not resenas:
            return {
                'success': True,
                'total': 0,
                'promedio': 0,
                'distribucion': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }

        total = len(resenas)
        suma = sum(r.valoracion for r in resenas)
        promedio = round(suma / total, 1)

        # Distribución por estrellas
        distribucion = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in resenas:
            if r.valoracion in distribucion:
                distribucion[r.valoracion] += 1

        return {
            'success': True,
            'total': total,
            'promedio': promedio,
            'distribucion': distribucion
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))