"""
Workana scraper placeholder - requer proxy residencial para funcionar.
"""
import logging
from typing import List

from playwright.async_api import Page

from core.base import ScraperBase
from core.models import Vaga

logger = logging.getLogger(__name__)

SEARCH_TERMS = [
    "Python automacao", "bot Telegram", "web scraping", "scraper Python",
    "Streamlit dashboard", "FastAPI", "Playwright", "BeautifulSoup",
    "automacao Python", "script Python", "bot Discord", "API integracao",
    "planilha automacao", "Google Sheets API"
]


class WorkanaScraper(ScraperBase):
    """Scraper para Workana - BLOQUEADO por Cloudflare em datacenter IPs.
    
    Para funcionar, precisa:
    - Proxy residencial (Bright Data, Oxylabs, Smartproxy) ~R$ 300-500/mês
    - CAPTCHA solver (2Captcha, Anti-Captcha) ~R$ 50-100/mês
    - Ou browser real persistente com cookies
    
    Esta implementação é placeholder para documentação.
    """
    
    @property
    def platform_name(self) -> str:
        return "workana"
    
    @property
    def search_terms(self) -> List[str]:
        return SEARCH_TERMS
    
    async def search(self, term: str) -> List[Vaga]:
        logger.warning(f"{self.platform_name}: Workana bloqueia datacenter IPs via Cloudflare.")
        logger.warning(f"{self.platform_name}: Necessário proxy residencial + CAPTCHA solver para funcionar.")
        logger.warning(f"{self.platform_name}: Retornando lista vazia. Configure proxy para ativar.")
        return []
    
    async def run_with_proxy(self, proxy_config: dict) -> List[Vaga]:
        """Método para usar com proxy residencial (futuro)."""
        # TODO: Implementar com proxy
        # self.page = await browser.new_page(proxy=proxy_config)
        # ...
        logger.info(f"{self.platform_name}: execução com proxy não implementada ainda")
        return []