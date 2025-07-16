import asyncio
import aiohttp
import constants as C

async def check_crossword(session, crid):
    url = f"https://www.theguardian.com/crosswords/cryptic/{crid}.json"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                return 1
            return 0
    except Exception:
        return 0

async def calculate_total_crosswords():
    missing = 0
    async with aiohttp.ClientSession() as session:
        tasks = [
            check_crossword(session, crid)
            for crid in range(C.MINIMUM_CROSSWORD_ID, C.MAXIMUM_CROSSWORD_ID)
        ]
        results = await asyncio.gather(*tasks)
        missing = sum(results)
        return missing

if __name__ == "__main__":
    missing = asyncio.run(calculate_total_crosswords())
    print(f"Total: {C.MAXIMUM_CROSSWORD_ID-missing}, Missing: {missing}")
