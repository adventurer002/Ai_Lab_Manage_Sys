from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.tools import tool

from app.common.exceptions import BusinessException
from app.model.user import User
from app.schemas.reservation import ReservationCreateRequest
from app.server import equipment_service, kb_service, lab_service, reservation_service


def build_tools(db: AsyncSession, current_user: User):

    @tool
    async def search_lab_docs(query: str) -> str:
        """根据用户的提问检索知识库（规则、安全、开放时间等文档）"""
        try:
            return await kb_service.search(query) or "没有检索到相关的资料"
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    async def list_open_labs(keywords: str = "") -> str:
        """查询当前开放中的实验室列表，可按名称关键字筛选"""
        try:
            keywords = keywords.strip() or None
            page = await lab_service.get_lab_list_service(
                db, page=1, page_size=20, keyword=keywords, status=1
            )
            rows = [
                {
                    "id": item.id,
                    "name": item.name,
                    "location": item.location,
                    "capacity": item.capacity,
                    "open_time": item.open_time,
                    "close_time": item.close_time,
                }
                for item in page.items
            ]
            return json.dumps(
                {"total": page.total, "labs": rows},
                ensure_ascii=False,
                default=str,
            )
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    async def list_lab_equipments(lab_id: int, keywords: str = "") -> str:
        """查询某个实验室下的设备列表。若不知道 lab_id，请先调用 list_open_labs 获取"""
        try:
            keywords = keywords.strip() or None
            page = await equipment_service.get_equipment_list_service(
                db, page=1, page_size=50, lab_id=int(lab_id), keyword=keywords
            )
            rows = [
                {
                    "id": item.id,
                    "name": item.name,
                    "lab_id": item.lab_id,
                    "lab_name": item.lab_name,
                    "spec": item.spec,
                    "quantity": item.quantity,
                    "status": "正常" if item.status == 1 else "维修中",
                }
                for item in page.items
            ]
            return json.dumps(
                {"total": page.total, "equipments": rows}, ensure_ascii=False
            )
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    async def create_lab_reservation(
        lab_id: int,
        date: str,
        start_time: str,
        end_time: str,
        equipment_id: int | None = None,
        remark: str | None = None,
    ) -> str:
        """创建预约单预约实验室或设备。调用前必须已向用户复述信息并获得确认"""
        try:
            data = ReservationCreateRequest(
                lab_id=lab_id,
                equipment_id=equipment_id,
                date=date,
                start_time=start_time,
                end_time=end_time,
                remark=remark,
            )
            await reservation_service.create_reservation_service(db, current_user, data)
            return json.dumps(
                {
                    "ok": True,
                    "message": "预约已提交，状态为待审核，请等待管理员审核通过",
                    "lab_id": lab_id,
                    "equipment_id": equipment_id,
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                },
                ensure_ascii=False,
            )
        except BusinessException as exc:
            return json.dumps({"ok": False, "error": exc.message}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)

    @tool
    async def get_today() -> str:
        """获取服务器当前日期，格式如 2026-09-20，用于换算今天/明天/后天"""
        return datetime.now().strftime("%Y-%m-%d")

    return [
        search_lab_docs,
        list_open_labs,
        list_lab_equipments,
        create_lab_reservation,
        get_today,
    ]
