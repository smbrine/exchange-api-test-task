import asyncio
import json
import datetime
import typing as t
from json import JSONDecodeError

import httpx

from utils.redis_wrapper import RedisWrapper


async def get_cb_division_rate(
    r: RedisWrapper,
    from_currency: str,
    to_currency: str,
    date_key: str,
    exchange_date: datetime.date = datetime.datetime.now().date(),
) -> float:
    """
    Returns currency exchange division rate according
    to the Central Bank of the Russian Federation.

    :param r: RedisWrapper for caching purposes
    :param from_currency: Currency to exchange from
    :param to_currency: Currency to exchange to
    :param date_key: Cache key
    :param exchange_date: Date to exchange at
    :return: Exchange division rate
    """
    if (
        raw_cb_rates := await r.hget(
            "cb_rates", date_key, encoding="utf-8"
        )
    ) is None:
        async with httpx.AsyncClient() as cl:
            raw_cb_rates = await cl.get(
                f"https://www.cbr-xml-daily.ru/archive"
                f"/{exchange_date.strftime('%Y/%m/%d')}/daily_json.js"
            )
            if not raw_cb_rates.is_success:
                url = "https://www.cbr-xml-daily.ru/daily_json.js"
                raw_cb_rates = await cl.get(url)
            raw_cb_rates = raw_cb_rates.text

        await r.hset("cb_rates", date_key, raw_cb_rates)

    cb_rates = json.loads(raw_cb_rates)

    match from_currency:
        case "RUB":
            division_rate = (
                cb_rates["Valute"][to_currency]["Value"]
                / cb_rates["Valute"][to_currency]["Nominal"]
            )
        case _:
            division_rate = (
                cb_rates["Valute"][from_currency]["Nominal"]
                / cb_rates["Valute"][from_currency]["Value"]
            )
    return division_rate


async def get_api_division_rate(
    r: RedisWrapper,
    from_currency: str,
    to_currency: str,
    date_key: str,
    exchange_date: datetime.date = datetime.datetime.now().date(),
) -> t.Optional[float]:
    """
    Returns currency exchange division rate according
    to https://github.com/fawazahmed0/exchange-api.

    :param r: RedisWrapper for caching purposes
    :param from_currency: Currency to exchange from
    :param to_currency: Currency to exchange to
    :param date_key: Cache key
    :param exchange_date: Date to exchange at
    :return: Exchange division rate
    """
    if raw_api_rates := await r.hget(
        f"api_rates:{from_currency}", date_key
    ):
        rates = json.loads(raw_api_rates)

        reverse_division_rate = rates[to_currency.lower()]
        division_rate = 1 / reverse_division_rate
        return division_rate

    async with httpx.AsyncClient() as cl:
        base_urls = ["cdn.jsdelivr.net", "currency-api.pages.dev"]
        full_url = (
            f"https://{base_urls[0]}/npm/@fawazahmed0/"
            f"currency-api@{exchange_date.strftime('%Y.%m')}."
            f"{exchange_date.day}/"
            f"v1/currencies/{from_currency.lower()}.json"
        )
        raw_api_response = (await cl.get(full_url)).text
    try:
        rates = json.loads(raw_api_response).get(from_currency.lower())
    except JSONDecodeError:
        return None

    await r.hset(f"api_rates:{from_currency}", date_key, json.dumps(rates))

    reverse_division_rate = rates.get(to_currency.lower())

    return 1 / reverse_division_rate


async def get_division_rate(
    r: RedisWrapper,
    from_currency: str,
    to_currency: str,
    exchange_date: datetime.date = datetime.datetime.now().date(),
) -> t.Optional[float]:
    """
    Returns currency exchange division rate according to
    multiple sources depending on the currencies one's working on.
    :param r: RedisWrapper for caching purposes
    :param from_currency: Currency to exchange from
    :param to_currency: Currency to exchange to
    :param exchange_date: Date to exchange at

    :return: Exchange division rate
    """
    name_key = f"{from_currency}:{to_currency}"
    reverse_name_key = f"{to_currency}:{from_currency}"
    date_key = exchange_date.strftime("%Y:%m:%d")

    if division_rate := await r.hget(name_key, date_key, encoding="utf-8"):
        return float(division_rate)

    if "RUB" in [from_currency, to_currency]:
        division_rate = await get_cb_division_rate(
            r, from_currency, to_currency, date_key, exchange_date
        )
    else:
        division_rate = await get_api_division_rate(
            r, from_currency, to_currency, date_key, exchange_date
        )

    if division_rate is None:
        return None

    reverse_division_rate = 1 / division_rate

    await asyncio.gather(
        r.hset(name_key, date_key, division_rate),
        r.hset(reverse_name_key, date_key, reverse_division_rate),
    )

    return division_rate
