from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy import select

from api.auth.auth_config import RoleChecker
from api.config.models import LiveSearchList
from db.session import get_db_general
from services.load_all_queries import get_all_data as get_all_data_queries

from services.load_all_urls import get_all_data as get_all_data_urls

from services.load_all_history import main as all_history_main

from services.load_query_url_merge import main as merge_main

from services.load_live_search import main as live_search_main

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get('/load-queries-script')
async def load_queries_script(
        request: Request,
        required: bool = Depends(RoleChecker(required_permissions={"Administrator", "Superuser"}))
):
    request_session = request.session
    res = await get_all_data_queries(request_session)
    if res["status"] == 400:
        raise HTTPException(status_code=400, detail="Нет новых обновлений")
    return {"status": 200}


@router.get('/load-urls-script')
async def load_urls_script(
        request: Request,
        required: bool = Depends(RoleChecker(required_permissions={"Administrator", "Superuser"}))
):
    request_session = request.session
    res = await get_all_data_urls(request_session)
    if res["status"] == 400:
        raise HTTPException(status_code=400, detail="Нет новых обновлений")
    return {"status": 200}


@router.get('/load-history-script')
async def load_history_script(
        request: Request,
        required: bool = Depends(RoleChecker(required_permissions={"Administrator", "Superuser"}))
) -> dict:
    try:
        request_session = request.session
        await all_history_main(request_session)
    except Exception as e:
        print(e)
    return {"status": 200}


@router.get('/load-merge-script')
async def load_merge_script(
        request: Request,
        required: bool = Depends(RoleChecker(required_permissions={"Administrator", "Superuser"}))
) -> dict:
    try:
        request_session = request.session
        await merge_main(request_session)
    except Exception as e:
        print(e)
    return {"status": 200}


@router.post('/load-live-search')
async def load_live_search_list(
    request: Request,
    list: dict,
    session: AsyncSession = Depends(get_db_general),
    required: bool = Depends(RoleChecker(required_permissions={"Administrator", "Superuser"}))
):
    list_id = int(list["list"])

    list_model = (await session.execute(select(LiveSearchList).where(LiveSearchList.id == list_id))).scalars().first()

    list_id, main_domain, lr, search_system = list_model.id, list_model.main_domain, list_model.lr, list_model.search_system

    await live_search_main(list_id, main_domain, lr, search_system, session)

    return {
        "status": 200,
    }




