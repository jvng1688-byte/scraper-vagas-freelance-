"""
Platforms package - scrapers para cada plataforma de freelance.
"""
from platforms.frelas99 import Freelas99Scraper
from platforms.workana import WorkanaScraper
from core.base import ScraperBase

__all__ = [
    "Freelas99Scraper",
    "WorkanaScraper",
]

# Registry de scrapers disponíveis
SCRAPERS = {
    "99freelas": Freelas99Scraper,
    "workana": WorkanaScraper,
}

def get_scraper(platform: str, page) -> ScraperBase:
    """Factory para obter scraper por nome."""
    if platform not in SCRAPERS:
        raise ValueError(f"Plataforma '{platform}' não suportada. Disponíveis: {list(SCRAPERS.keys())}")
    return SCRAPERS[platform](page)