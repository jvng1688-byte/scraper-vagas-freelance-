"""
Scraper Vagas Freelance - Orquestrador Modular
Usa scrapers por plataforma (99freelas, workana, etc.) via core/base + platforms/.
"""
import os
import asyncio
import logging
from datetime import datetime
from typing import List

from playwright.async_api import async_playwright
from dotenv import load_dotenv

from core.models import Vaga
from core.exporters import save_to_excel, save_to_csv, sync_notion
from platforms import get_scraper, SCRAPERS

load_dotenv()

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Plataformas ativas (descomente workana quando tiver proxy)
ACTIVE_PLATFORMS = ["99freelas"]  # , "workana"]


async def run_all_scrapers() -> List[Vaga]:
    """Roda todos os scrapers ativos e retorna vagas únicas ordenadas por score."""
    all_vagas = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="pt-BR",
            timezone_id="America/Sao_Paulo"
        )
        page = await context.new_page()

        for platform_name in ACTIVE_PLATFORMS:
            try:
                scraper = get_scraper(platform_name, page)
                logger.info(f"Iniciando scraper: {platform_name}")
                vagas = await scraper.run_all_terms()
                all_vagas.extend(vagas)
                logger.info(f"{platform_name}: {len(vagas)} vagas coletadas")
            except Exception as e:
                logger.error(f"Erro no scraper {platform_name}: {e}")

        await browser.close()

    # Remove duplicatas por URL
    seen = set()
    unique_vagas = []
    for v in all_vagas:
        if v.url not in seen:
            seen.add(v.url)
            unique_vagas.append(v)

    # Ordena por score desc
    unique_vagas.sort(key=lambda x: x.score, reverse=True)
    logger.info(f"Total vagas unicas: {len(unique_vagas)}")
    return unique_vagas


async def main():
    logger.info("Iniciando scraper de vagas freelance (modular)...")
    vagas = await run_all_scrapers()
    if not vagas:
        logger.warning("Nenhuma vaga encontrada")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    save_to_excel(vagas, f"vagas_freelance_{timestamp}.xlsx")
    save_to_csv(vagas, f"vagas_freelance_{timestamp}.csv")
    await sync_notion(vagas, NOTION_TOKEN, NOTION_DATABASE_ID)

    print("\n" + "=" * 80)
    print(f"TOP 5 VAGAS (score 0-100) - {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 80)
    for i, v in enumerate(vagas[:5], 1):
        print(f"\n{i}. [{v.plataforma}] Score: {v.score:.1f}/100")
        print(f"   {v.titulo}")
        print(f"   {v.orcamento} | {v.prazo} | {v.propostas} propostas")
        print(f"   Cliente: {v.cliente_avaliacao}/5 ({v.cliente_projetos} projetos) | {v.cliente_pagamentos}")
        print(f"   {v.url}")
        print(f"   Skills: {', '.join(v.habilidades[:8])}")
    print(f"\nTotal: {len(vagas)} vagas unicas | Arquivos salvos com timestamp {timestamp}")


if __name__ == "__main__":
    asyncio.run(main())