from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import engine, Base

# =========================================================
# MODELS
# =========================================================

from models.user import User
from models.report import Report
from models.publication import Publication
from models.dataset import Dataset
from models.image import Image
from models.video import Video
from models.activity import Activity
from models.expedition import Expedition
from models.resource import Resource


# =========================================================
# ROUTERS
# =========================================================

from routers.user import router as user_router
from routers.report import router as report_router
from routers.publication import router as publication_router
from routers.resource import router as resource_router
from routers.admin import router as admin_router
from routers.auth import router as auth_router
from routers.dataset import router as dataset_router
from routers.image import router as image_router
from routers.video import router as video_router
from routers.activity import router as activity_router
from routers.expedition import router as expedition_router


# =========================================================
# STORAGE
# =========================================================

from storage.minio_client import create_bucket_if_not_exists


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="PolarConnect API",
    description="Integrated Polar Science Outreach, Knowledge Repository and Media Dissemination Portal",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(user_router)
app.include_router(report_router)
app.include_router(publication_router)
app.include_router(resource_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(dataset_router)
app.include_router(image_router)
app.include_router(video_router)
app.include_router(activity_router)
app.include_router(expedition_router)


# =========================================================
# DATABASE + MINIO INITIALIZATION
# =========================================================

Base.metadata.create_all(bind=engine)

create_bucket_if_not_exists()


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "PolarConnect Backend is Running"
    }


# =========================================================
# DATABASE TEST
# =========================================================

@app.get("/test-db")
def test_database():

    try:

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT 1")
            )

            return {
                "status": "success",
                "message": "PostgreSQL connected successfully",
                "result": result.scalar()
            }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }