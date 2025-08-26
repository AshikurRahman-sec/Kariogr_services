from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from typing import Union
import requests
import logging
import os

import schemas.userAndsetting_schemas as _schemas
from utils.response_builder import build_response  # Ensure this function is available
from dependencies import verify_token

USER_SETTINGS_BASE_URL = os.environ.get("USER_SETTINGS_BASE_URL")

router = APIRouter()

@router.post(
    "/create/unregister_user_address",
    response_model=Union[_schemas.AddressResponse, _schemas.ErrorResponse],
)
async def create_address_gateway(request_data: _schemas.AddressRequestBody):
    """
    Gateway API to forward the `create_address` request to the Address microservice.
    """
    try:
        address_data = jsonable_encoder(request_data.body)

        response = requests.post(f"{USER_SETTINGS_BASE_URL}/api/create/unregister_user_address", json=address_data)

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Address created successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to create address"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Address microservice is unavailable")
        return build_response(
            data={},
            message="Address microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )


@router.post(
    "/worker-zones",
    response_model=Union[_schemas.WorkerZoneResponse,  _schemas.ErrorResponse]
)
async def get_worker_zones_gateway(
    request_data: _schemas.WorkerZoneRequestBody,
    user: dict = Depends(verify_token),
):
    """
    Gateway API that forwards the `get_worker_zones_by_skill` request to the Worker microservice.
    """
    try:
        service_id = request_data.body.service_id 

        response = requests.get(
            f"{USER_SETTINGS_BASE_URL}/api/worker_zones/{service_id}"
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Worker zones retrieved successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch worker zones"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker microservice is unavailable")
        return build_response(
            data={},
            message="Worker microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/workers/filter",
    response_model=Union[_schemas.WorkerFilterGatewayResponse, _schemas.ErrorResponse]
)
async def get_workers_by_skill_and_district_gateway(
    request_data: _schemas.WorkerFilterGatewayRequest,
    limit: int = Query(10, ge=1),  # Default limit: 10, min: 1
    offset: int = Query(0, ge=0),  # Default offset: 0, min: 0
    user: dict = Depends(verify_token),  # Auth validation
):
    """
    Gateway API that forwards the `get_workers_by_skill_and_district` request to the Worker microservice.
    Supports pagination using limit and offset.
    """
    try:
        # Forward request to the worker microservice
        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/workers/filter",
            json={
                "skill_id": request_data.body.skill_id,
                "district": request_data.body.district,
                "user_id": user["user_id"]
            },
            params={"limit": limit, "offset": offset},  # Pass limit & offset as query parameters
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data["data"],
                request_id=request_data.header.requestId,
                message="Workers retrieved successfully",
                code="200",
                meta={  # Include pagination metadata
                    "page": response_data["page"],
                    "size": response_data["size"],
                    "total_services": response_data["total_services"]
                },
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch workers"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker microservice is unavailable")
        return build_response(
            data={},
            message="Worker microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )



@router.post(
    "/workers/by-zone",
    response_model=Union[_schemas.WorkerByZoneGatewayResponse, _schemas.ErrorResponse]
)
async def get_workers_by_zone_gateway(
    request_data: _schemas.WorkerByZoneGatewayRequest,
    page: int = Query(0, ge=0),   # Default page: 0, minimum: 0
    size: int = Query(10, ge=1),  # Default size: 10, minimum: 1
    user: dict = Depends(verify_token),  # Auth validation
):
    """
    Gateway API that forwards the `get_workers_by_zone` request to the Worker microservice.
    Supports pagination using `page` and `size` query parameters.
    """
    try:
        # Forward request to the Worker microservice
        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/workers/by-zone",
            json={
                "worker_id": request_data.body.worker_id,
                "district": request_data.body.district
            },
            params={"page": page, "size": size},  # Pass pagination params
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data["data"],
                request_id=request_data.header.requestId,
                message="Workers retrieved successfully",
                code="200",
                meta={
                    "page": response_data["page"],
                    "size": response_data["size"],
                    "total_workers": response_data["total_workers"]
                },
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch workers"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker microservice is unavailable")
        return build_response(
            data={},
            message="Worker microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/worker-skill-rating",
    response_model=_schemas.CreateWorkerSkillRatingResponse,
)
async def create_worker_skill_rating_gateway(
    request_data: _schemas.CreateWorkerSkillRatingRequest,
    user: dict = Depends(verify_token),
):
    try:
        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/worker-skill-rating",
            json=request_data.body.dict(),
        )

        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Worker skill rating submitted successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to submit worker rating"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker service is unavailable")
        return build_response(
            data={},
            message="Worker service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/worker-details",
    response_model=_schemas.WorkerDetailsGatewayResponse,
)
async def get_worker_details_gateway(
    request_data: _schemas.WorkerDetailsGatewayRequest,
    #user: dict = Depends(verify_token),
):
    try:
        worker_id = request_data.body.worker_id
        skill_id = request_data.body.skill_id

        # Call the service
        response = requests.get(
            f"{USER_SETTINGS_BASE_URL}/api/worker_details/{worker_id}/{skill_id}",
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Worker details retrieved successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to retrieve worker details"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Worker service is unavailable")
        return build_response(
            data={},
            message="Worker service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/post-comment",
    response_model=_schemas.CommentGatewayResponse,
)
async def post_comment_gateway(
    request_data: _schemas.CommentGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        body_data = request_data.body.dict()
        body_data["user_id"] = user["user_id"]  # Insert user_id into body

        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/post-comment",
            json=body_data,
        )

        if response.status_code in (200, 201):
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Comment posted successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to post comment"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Comment service is unavailable")
        return build_response(
            data={},
            message="Comment service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/get-comment",
    response_model=_schemas.CommentListGatewayResponse,
)
async def get_comments_gateway(
    request_data: _schemas.CommentListGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        worker_id = request_data.body.worker_id
        skill_id = request_data.body.skill_id
        limit = request_data.body.limit
        offset = request_data.body.offset

        response = requests.get(
            f"{USER_SETTINGS_BASE_URL}/api/get-comment/{worker_id}/{skill_id}",
            params={"limit": limit, "offset": offset},
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Comments fetched successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch comments"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Comment service is unavailable")
        return build_response(
            data={},
            message="Comment service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )
    
@router.post(
    "/comment-replies",
    response_model=_schemas.CommentListGatewayResponse,
)
async def get_comment_replies_gateway(
    request_data: _schemas.CommentReplyListGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        parent_comment_id = request_data.body.parent_comment_id
        limit = request_data.body.limit
        offset = request_data.body.offset

        response = requests.get(
            f"{USER_SETTINGS_BASE_URL}/api/comment/replies/{parent_comment_id}",
            params={"limit": limit, "offset": offset},
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Replies fetched successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to fetch replies"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Comment service is unavailable")
        return build_response(
            data={},
            message="Comment service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/comment-reaction",
    response_model=_schemas.CommentReactionGatewayResponse,
)
async def comment_reaction_gateway(
    request_data: _schemas.CommentReactionGatewayRequest,
    user: dict = Depends(verify_token),
):
    try:
        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/comment/reaction",
            json=request_data.body.dict(),
        )

        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Reaction submitted successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to submit reaction"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("Comment service is unavailable")
        return build_response(
            data={},
            message="Comment service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post(
    "/worker/bookmark",
    response_model=Union[_schemas.WorkerBookmarkResponse, _schemas.ErrorResponse],
)
async def create_worker_bookmark_gateway(request_data: _schemas.WorkerBookmarkRequestBody,
                                         user: dict = Depends(verify_token)):
    """
    Gateway API to forward the `add_worker_bookmark` request to the WorkerBookmark microservice.
    """
    try:
        response = requests.post(
            f"{USER_SETTINGS_BASE_URL}/api/worker/bookmark",
            json={"user_id":user["user_id"], "worker_id":request_data.body.worker_id}
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Worker bookmarked successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to bookmark worker"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("WorkerBookmark microservice is unavailable")
        return build_response(
            data={},
            message="WorkerBookmark microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.delete(
    "/worker/bookmark",
    response_model=Union[dict, _schemas.ErrorResponse]
)
async def delete_worker_bookmark_gateway(request_data: _schemas.WorkerBookmarkRequestBody,
                                         user: dict = Depends(verify_token)):
    """
    Gateway API to forward the `remove_worker_bookmark` request to the WorkerBookmark microservice.
    """
    try:
        response = requests.delete(
            f"{USER_SETTINGS_BASE_URL}/api/worker/bookmark",
            params={"user_id": user["user_id"], "worker_id": request_data.body.worker_id}
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Worker bookmark removed successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail", "Failed to remove bookmark"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("WorkerBookmark microservice is unavailable")
        return build_response(
            data={},
            message="WorkerBookmark microservice is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )


@router.get(
    "/worker/bookmarks",
    response_model=Union[_schemas.WorkerBookmarkResponse, _schemas.ErrorResponse],
)
async def list_worker_bookmarks_gateway(user_id: str, request_id: str):
    """
    Gateway API to forward the `list_worker_bookmarks` request to the WorkerBookmark microservice.
    """
    try:
        response = requests.get(
            f"{USER_SETTINGS_BASE_URL}/api/worker/bookmarks",
            params={"user_id": user_id}
        )

        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_id,
                message="Worker bookmarks retrieved successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_id,
                message=response.json().get("detail", "Failed to fetch bookmarks"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        logging.error("WorkerBookmark microservice is unavailable")
        return build_response(
            data={},
            message="WorkerBookmark microservice is unavailable",
            code="503",
            request_id=request_id,
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_id,
        )
