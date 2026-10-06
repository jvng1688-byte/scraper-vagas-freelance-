"""
99freelas scraper implementation.
"""
import asyncio
import logging
import re
from typing import List

from playwright.async_api import Page

from core.base import ScraperBase
from core.models import Vaga, calculate_score

logger = logging.getLogger(__name__)

SEARCH_TERMS = [
    "Python automacao", "bot Telegram", "web scraping", "scraper Python",
    "Streamlit dashboard", "FastAPI", "Playwright", "BeautifulSoup",
    "automacao Python", "script Python", "bot Discord", "API integracao",
    "planilha automacao", "Google Sheets API"
]


class Freelas99Scraper(ScraperBase):
    """Scraper para 99freelas.com.br - busca pública sem login."""
    
    @property
    def platform_name(self) -> str:
        return "99freelas"
    
    @property
    def search_terms(self) -> List[str]:
        return SEARCH_TERMS
    
    async def search(self, term: str) -> List[Vaga]:
        vagas = []
        try:
            search_url = f"https://www.99freelas.com.br/projects?search={term.replace(' ', '%20')}"
            await self.page.goto(search_url, wait_until="networkidle")
            
            # Check for Cloudflare challenge
            body_text = await self.page.inner_text("body")
            if "verificação de segurança" in body_text.lower() or "captcha" in body_text.lower() or "cloudflare" in body_text.lower():
                logger.warning(f"{self.platform_name}: possível bloqueio Cloudflare/challenge detectado")
                return vagas
            
            # Scroll to load lazy content
            logger.info(f"{self.platform_name}: rolando página...")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
            # Find project list container - try multiple selectors
            project_list = None
            container_selectors = [
                ".box-projects .projects-list",
                ".box-projects",
                ".search-results",
                ".projects-list",
                "[data-testid='projects-list']",
                ".projects-grid",
                "main .box-projects"
            ]
            
            for sel in container_selectors:
                try:
                    project_list = await self.page.query_selector(sel)
                    if project_list:
                        logger.info(f"{self.platform_name}: container encontrado: {sel}")
                        break
                except:
                    continue
            
            if not project_list:
                # Fallback: use body
                project_list = self.page
                logger.warning(f"{self.platform_name}: container específico não encontrado, usando body")
            
            # Search for project cards within container
            # Strategy: find all project links, then get their parent card elements
            project_links = await project_list.query_selector_all("a[href*='/project/']")
            
            cards = []
            seen_urls = set()
            for link in project_links[:40]:  # check more links
                try:
                    url = await link.get_attribute("href")
                    if not url or '/project/' not in url or '/project/new' in url:
                        continue
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    # Get parent card element (go up to find container with project data)
                    # Try multiple ancestor levels
                    card = None
                    for ancestor_level in range(1, 6):
                        try:
                            ancestor = await link.query_selector(f"xpath=ancestor::*[{ancestor_level}][contains(@class, 'item') or contains(@class, 'card') or contains(@class, 'project') or contains(@class, 'box')]")
                            if ancestor:
                                # Check if this ancestor has meaningful content (more than just the link)
                                text = await ancestor.inner_text()
                                if len(text.strip()) > 50:  # has substantial content
                                    card = ancestor
                                    break
                        except:
                            continue
                    
                    if card:
                        cards.append(card)
                        if len(cards) >= 20:
                            break
                except:
                    continue
            
            if not cards:
                logger.warning(f"{self.platform_name}: nenhum card válido encontrado para '{term}'")
                return vagas
            
            logger.info(f"{self.platform_name}: {len(cards)} cards válidos encontrados")
            
            # DEBUG: log first few card URLs
            for i, card in enumerate(cards[:5]):
                try:
                    link_el = await card.query_selector("a[href*='/project/']")
                    if link_el:
                        url = await link_el.get_attribute("href")
                        if url and not url.startswith("http"):
                            url = f"https://www.99freelas.com.br{url}"
                        logger.info(f"{self.platform_name}: Card {i+1} URL: {url}")
                except:
                    pass
            
            # Parse cards
            for card in cards[:30]:
                try:
                    # Título e URL
                    titulo_el = await card.query_selector("a[href*='/project/'], h3 a, h2 a, .title a")
                    titulo = await titulo_el.inner_text() if titulo_el else "Sem titulo"
                    url = await titulo_el.get_attribute("href") if titulo_el else ""
                    if url and not url.startswith("http"):
                        url = f"https://www.99freelas.com.br{url}"
                    
                    # Filtra ruído
                    if not url or '/project/' not in url or '/project/new' in url:
                        continue
                    if titulo.strip().lower() in ["publique um projeto. é grátis.", "publique um projeto", "novo projeto"]:
                        continue
                    
                    # Descrição
                    desc_el = await card.query_selector("[data-testid='description'], .description, .project-description, .formatted-text, p")
                    descricao = await desc_el.inner_text() if desc_el else ""
                    
                    # Orçamento
                    orc_el = await card.query_selector("[data-testid='budget'], .budget, .value, .price, [class*='budget']")
                    orcamento = await orc_el.inner_text() if orc_el else "Nao informado"
                    
                    # Prazo
                    prazo_el = await card.query_selector("[data-testid='deadline'], .deadline, .time, [class*='deadline']")
                    prazo = await prazo_el.inner_text() if prazo_el else "Nao informado"
                    
                    # Skills
                    skills_els = await card.query_selector_all("[data-testid='skill'], .tag, .skill, [class*='skill'], [class*='tag']")
                    habilidades = [await s.inner_text() for s in skills_els]
                    
                    # Propostas
                    prop_el = await card.query_selector("[data-testid='proposals'], .proposals, .count, [class*='proposal']")
                    propostas_text = await prop_el.inner_text() if prop_el else "0"
                    propostas = int(''.join(filter(str.isdigit, propostas_text))) if propostas_text else 0
                    
                    # Cliente
                    cliente_el = await card.query_selector("[data-testid='client'], .client, .user, [class*='client']")
                    cliente_text = await cliente_el.inner_text() if cliente_el else ""
                    aval_match = re.search(r"(\d[.,]\d)", cliente_text)
                    avaliacao = float(aval_match.group(1).replace(",", ".")) if aval_match else 0
                    proj_match = re.search(r"(\d+)\s*projet", cliente_text, re.I)
                    projetos = int(proj_match.group(1)) if proj_match else 0
                    
                    vaga = Vaga(
                        plataforma=self.platform_name,
                        titulo=titulo.strip(),
                        descricao=descricao.strip()[:500],
                        orcamento=orcamento.strip(),
                        prazo=prazo.strip(),
                        habilidades=habilidades,
                        propostas=propostas,
                        cliente_avaliacao=avaliacao,
                        cliente_projetos=projetos,
                        cliente_pagamentos="Verificado" if "verificado" in cliente_text.lower() else "Nao verificado",
                        url=url,
                        data_coleta=__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M")
                    )
                    vaga.score = calculate_score(vaga)
                    vagas.append(vaga)
                    
                except Exception as e:
                    logger.debug(f"Erro parse card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"{self.platform_name}: erro ao buscar '{term}': {e}")
            
        return vagas