from fastapi import APIRouter

router = APIRouter(
    prefix="/api/resources",
    tags=["Resources"]
)


resources = [
    {
        "id": 1,
        "title": "Antarctic Expedition Report 2025",
        "resource_type": "Report",
        "year": 2025,
        "location": "Antarctica"
    },
    {
        "id": 2,
        "title": "Polar Climate Research",
        "resource_type": "Publication",
        "year": 2024,
        "location": "Antarctica"
    }
]


@router.get("/")
def get_resources():
    return resources