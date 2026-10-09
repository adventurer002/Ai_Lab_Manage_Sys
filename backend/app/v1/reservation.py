from fastapi import APIRouter, Depends

from app.common.response import Response
from app.database import get_async_session
from app.dependencies.auth import get_current_user, judge_manager
from app.model.user import User
from app.schemas.reservation import ReservationCreateRequest, AuditReservationRequest
from app.server import reservation_service
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/reservation", tags=["预约相关接口"])


@router.post("")
async def create_reservation(
    data: ReservationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    await reservation_service.create_reservation_service(db, current_user, data)
    return Response.success()


# reserve list列表
@router.get("/list")
async def get_reservation_list(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 10,
    status: int | None = None,
):
    res = await reservation_service.get_reservation_list_service(
        db, current_user, page, page_size, status
    )
    return Response.success(data=res)


# 取消预约
@router.put("/{reservation_id}/cancel")
async def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    await reservation_service.cancel_reservation_service(
        db, current_user, reservation_id
    )
    return Response.success()


# audit审查预约
@router.put("/{reservation_id}/audit")
async def audit_reservation(
    reservation_id: int,
    data: AuditReservationRequest,
    current_user: User = Depends(judge_manager),
    db: AsyncSession = Depends(get_async_session),
):
    await reservation_service.audit_reservation_service(db, reservation_id, data.status)
    return Response.success()
