from fastapi import APIRouter, Request, Response

from src.config import BOOKING_SERVICE_URL
from src.utils.http_client import client

router = APIRouter(prefix="/booking")


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_booking(request: Request, path: str) -> Response:
    """Proxy requests to the Booking Service.

    Args:
        request (Request): The incoming FastAPI request.
        path (str): The path to be appended to the Booking Service URL.

    Returns:
        Response: The response from the Booking Service.

    """
    path = path.rstrip("/")
    query_string = request.url.query
    url = f"{BOOKING_SERVICE_URL}/{path}"
    if query_string:
        url = f"{url}?{query_string}"

    body = await request.body()

    downstream_response = await client.request(
        method=request.method,
        url=url,
        headers=request.headers.raw,
        content=body,
    )

    return Response(
        content=downstream_response.content,
        status_code=downstream_response.status_code,
        headers=dict(downstream_response.headers),
        media_type=downstream_response.headers.get("content-type"),
    )
