from fastapi import APIRouter, HTTPException, Query, Depends
from uuid import UUID
import requests, os

from utils.response_builder import build_response
from schemas.service_schemas import *
from dependencies import verify_token

router = APIRouter()

SERVICE_BASE_URL = os.environ.get("SERVICE_BASE_URL")


# POST-based functions
@router.post("/root-services/")
async def get_root_services_gateway(
    request_data: ServiceRequestBody,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
    user: dict = Depends(verify_token),  
):
    """
    Gateway API that verifies token via Auth Service before forwarding request.
    """

    try:
        response = requests.get(
            f"{SERVICE_BASE_URL}/api/root-services/",
            params={"page": page, "size": size},
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Request successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(message="Service is unavailable", code="503", request_id=request_data.header.requestId)
    except Exception as e:
        return build_response(message=f"Unexpected error: {str(e)}", code="500", request_id=request_data.header.requestId)


@router.post("/second-level-services/")
async def get_second_level_services_gateway(
    request_data: ServiceIdRequestBody,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
    user: dict = Depends(verify_token), 
):
    """
    Gateway API to forward the `get_second_level_services` request to the corresponding microservice.
    """
    try:
        # Calculate offset
        offset = (page - 1) * size
        
        # Extract service ID from the request body
        service_id = request_data.body.service_id
        
        # Forward request to the microservice
        response = requests.get(
            f"{SERVICE_BASE_URL}/api/second-level-services/{service_id}",
            params={"offset": offset, "limit": size},
        )
        
        # Handle response
        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Request successful",
                code="200",
            )
        else:
            # Error response from microservice
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        # Service unavailable
        return build_response(
            message="Service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        # Unexpected error
        return build_response(
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post("/service/details/")
async def get_service_details_gateway(
    request_data: ServiceIdRequestBody,
    user: dict = Depends(verify_token), 
):
    try:

        # Extract service ID from the request body
        service_id = request_data.body.service_id

        response = requests.get(f"{SERVICE_BASE_URL}/api/service/{service_id}/details/")
        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Request successful",
                code="200",
            )
        elif response.status_code == 404:
            return build_response(
                message=f"Service with ID {service_id} not found.",
                code="404",
                request_id=request_data.header.requestId,
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            message="Service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post("/special-services/")
async def get_special_services_gateway(
    request_header: RequestHeader,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
    user: dict = Depends(verify_token), 
):
    try:
        response = requests.get(
            f"{SERVICE_BASE_URL}/api/special-services/",
            params={"page": page, "size": size},
        )
        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_header.requestId,
                message="Request successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            message="Service is unavailable",
            code="503",
            request_id=request_header.requestId,
        )
    except Exception as e:
        return build_response(
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_header.requestId,
        )

@router.post("/search-services/")
async def get_search_services_gateway(
    request_header: RequestHeader,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
    user: dict = Depends(verify_token), 
):
    try:
        response = requests.get(
            f"{SERVICE_BASE_URL}/api/search-services/",
            params={"page": page, "size": size},
        )
        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_header.requestId,
                message="Request successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(
            message="Service is unavailable",
            code="503",
            request_id=request_header.requestId,
        )
    except Exception as e:
        return build_response(
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_header.requestId,
        )

@router.post("/service/hierarchy/",)
async def get_descendant_hierarchy_gateway(
    request_data: ServiceIdRequestBody,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, description="Page size"),
    user: dict = Depends(verify_token), 
):
    """
    Gateway API to forward the `get_descendant_hierarchy` request to the corresponding microservice.
    """
    try:
        # Extract service details from the request body
        service_id = request_data.body.service_id

        # Forward the request to the microservice
        response = requests.get(
            f"{SERVICE_BASE_URL}/api/service/{service_id}/hierarchy/",
            params={"page": page, "size": size},
        )

        # Handle the microservice response
        if response.status_code == 200:
            response_data = response.json()
            return build_response(
                data=response_data,
                request_id=request_data.header.requestId,
                message="Hierarchy fetched successfully",
                code="200",
            )
        else:
            return build_response(
                data={},
                request_id=request_data.header.requestId,
                message=response.json().get("detail"),
                code=str(response.status_code),
            )

    except requests.exceptions.ConnectionError:
        return build_response(
            data={},
            message="Service is unavailable",
            code="503",
            request_id=request_data.header.requestId,
        )
    except Exception as e:
        return build_response(
            data={},
            message=f"An unexpected error occurred: {str(e)}",
            code="500",
            request_id=request_data.header.requestId,
        )

@router.post("/booking_inputs/")
async def get_booking_inputs_by_service_gateway(
    request_data: ServiceIdRequestBody,  # Use the correct request body structure
    user: dict = Depends(verify_token),
):
    """
    Gateway API that verifies token via Auth Service before forwarding request.
    """

    try:
        service_id = request_data.body.service_id  # Extract service_id correctly
        if not service_id:
            return build_response(
                message="Missing 'service_id' in request body",
                code="400",
                request_id=request_data.header.requestId,
            )

        response = requests.get(
            f"{SERVICE_BASE_URL}/api/booking_inputs/{service_id}"  # Forward service_id in the URL
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Request successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(message="Service is unavailable", code="503", request_id=request_data.header.requestId)
    except Exception as e:
        return build_response(message=f"Unexpected error: {str(e)}", code="500", request_id=request_data.header.requestId)
    
@router.post("/preferred_services/")
async def get_service_relatives_gateway(
    request_data: ServiceIdRequestBody,  # Use structured request body
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    user: dict = Depends(verify_token),
):
    """
    Gateway API that verifies token via Auth Service before forwarding request.
    """

    try:
        service_id = request_data.body.service_id  # Extract service_id from request body
        if not service_id:
            return build_response(
                message="Missing 'service_id' in request body",
                code="400",
                request_id=request_data.header.requestId,
            )

        response = requests.get(
            f"{SERVICE_BASE_URL}/api/{service_id}/relatives",
            params={"page": page, "size": size},  # Pass page and size as query parameters
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Request successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(message="Service is unavailable", code="503", request_id=request_data.header.requestId)
    except Exception as e:
        return build_response(message=f"Unexpected error: {str(e)}", code="500", request_id=request_data.header.requestId)

@router.post("/second-level-with-child/")
async def second_level_services_with_child(
    request_data: ServiceRequestBody,  # Standard request body structure
    limit: int = Query(10, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    user: dict = Depends(verify_token),
):
    """
    Gateway API that verifies token via Auth Service before forwarding request.
    """

    try:
        response = requests.get(
            f"{SERVICE_BASE_URL}/api/second-level",
            params={"limit": limit, "offset": offset},  # Pass pagination as query parameters
        )

        if response.status_code == 200:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Request successful",
                code="200",
            )
        else:
            return build_response(
                data=response.json(),
                request_id=request_data.header.requestId,
                message="Error from microservice",
                code=str(response.status_code),
            )
    except requests.exceptions.ConnectionError:
        return build_response(message="Service is unavailable", code="503", request_id=request_data.header.requestId)
    except Exception as e:
        return build_response(message=f"Unexpected error: {str(e)}", code="500", request_id=request_data.header.requestId)

