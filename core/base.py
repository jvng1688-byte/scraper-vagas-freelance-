"""
Base scraper class for freelance platforms.
"""
import logging
from abc import ABC, abstractmethod
from typing import List

from playwright.async_api import Page

from core.models import Vaga

logger = logging.getLogger(__name__)


class ScraperBase(ABC):
    """Classe base para scrapers de plataformas de freelance."""
    
    def __init__(self, page: Page):
        self.page = page
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Nome da plataforma (ex: '99freelas', 'workana')."""
        pass
    
    @property
    @abstractmethod
    def search_terms(self) -> List[str]:
        """Termos de busca para esta plataforma."""
        pass
    
    @abstractmethod
    async def search(self, term: str) -> List[Vaga]:
        """Busca vagas para um termo específico."""
        pass
    
    async def run_all_terms(self) -> List[Vaga]:
        """Roda busca para todos os termos configurados."""
        all_vagas = []
        for term in self.search_terms:
            try:
                logger.info(f"{self.platform_name}: buscando '{term}'")
                vagas = await self.search(term)
                all_vagas.extend(vagas)
            except Exception as e:
                logger.error(f"{self.platform_name}: erro ao buscar '{term}': {e}")
        return all_vagas