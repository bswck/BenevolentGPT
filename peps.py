from __future__ import annotations
import asyncio
import aiohttp
from pathlib import Path
from typing import TYPE_CHECKING
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from collections.abc import Mapping

pep_api_url = "https://peps.python.org/api/peps.json"
output_dir = Path("downloaded_peps")
output_dir.mkdir(parents=True, exist_ok=True)

async def fetch_pep(session: aiohttp.ClientSession, pep_number: int, pep_url: str) -> None:
    pep_filename: Path = output_dir / f"pep-{pep_number:04d}.html"
    text_filename: Path = output_dir / f"pep-{pep_number:04d}.txt"
    
    try:
        async with session.get(pep_url) as response:
            response.raise_for_status()
            content = await response.text()
            soup = BeautifulSoup(content, "html.parser")

            # Extract the content of the PEP
            pep_content = soup.find("section", id="pep-content")
            if pep_content:
                # Save the extracted content as plain text
                with text_filename.open("w", encoding="utf-8") as file:
                    file.write(pep_content.get_text())
                print(f"Extracted and saved PEP {pep_number}: {text_filename.name}")
            else:
                print(f"Failed to extract content from PEP {pep_number}: content section not found")

    except aiohttp.ClientError as e:
        print(f"Failed to download PEP {pep_number}: {e}")

async def fetch_all_peps(peps: Mapping[str, object]) -> None:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for pep_num, pep_info in peps.items():
            pep_url: str | None = pep_info.get("url")
            if pep_url:
                tasks.append(fetch_pep(session, int(pep_num), pep_url))
            else:
                print(f"PEP {pep_info['number']} does not have a valid URL, skipping...")

        await asyncio.gather(*tasks)

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(pep_api_url) as response:
            peps: Mapping[str, object] = await response.json()

    await fetch_all_peps(peps)

if __name__ == "__main__":
    asyncio.run(main())