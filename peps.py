from __future__ import annotations

import asyncio
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

import aiofiles
import aiohttp
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from collections.abc import Mapping

PEP_API_URL = "https://peps.python.org/api/peps.json"
output_dir = Path("downloaded_peps")
output_dir.mkdir(parents=True, exist_ok=True)


async def fetch_pep(
    session: aiohttp.ClientSession,
    pep_number: int,
    pep_url: str,
) -> None:
    text_filename: Path = output_dir / f"pep-{pep_number:04d}.txt"

    with suppress(aiohttp.ClientError):
        async with session.get(pep_url) as response:
            response.raise_for_status()
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")

            pep_content = soup.find("section", id="pep-content")
            if pep_content:
                async with aiofiles.open(text_filename, "w", encoding="utf-8") as file:
                    await file.write(pep_content.get_text())
                    await aiofiles.stdout.write(f"Wrote {text_filename}\n")
                    await aiofiles.stdout.flush()


async def fetch_all_peps(peps: Mapping[str, object]) -> None:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for pep_num, pep_info in peps.items():
            pep_url: str | None = pep_info.get("url")
            if pep_url:
                tasks.append(fetch_pep(session, int(pep_num), pep_url))

        await asyncio.gather(*tasks)


async def main() -> None:
    async with aiohttp.ClientSession() as session, session.get(PEP_API_URL) as response:
        peps: Mapping[str, object] = await response.json()

    await fetch_all_peps(peps)


if __name__ == "__main__":
    asyncio.run(main())
