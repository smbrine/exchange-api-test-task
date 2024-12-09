import typing as t

from fastapi import APIRouter, Query, Depends, HTTPException
from starlette.responses import JSONResponse

from app.dependencies import get_redis
from app.v1 import schemas
from app.v1.utils import get_division_rate
from utils.redis_wrapper import RedisWrapper

router = APIRouter()


@router.get("/rates")
async def handle_get_rates(
    params: t.Annotated[schemas.RatesParams, Query()],
    r: t.Annotated[RedisWrapper, Depends(get_redis)],
):
    division_rate = await get_division_rate(
        r, params.from_, params.to, params.date
    )

    if not division_rate:
        raise HTTPException(
            400, "Could not find one of the specified currencies (or neither of them)."
        )

    return JSONResponse({"result": round(params.value / division_rate, 2)})
