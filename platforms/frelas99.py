"""
99freelas scraper implementation.
"""
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

            # DEBUG: log page title, URL, and body snippet
            page_title = await self.page.title()
            logger.info(f"{self.platform_name}: page title: {page_title}")
            logger.info(f"{self.platform_name}: current URL: {self.page.url}")
            
            # DEBUG: check if we're on a challenge/blocked page
            body_text = await self.page.inner_text("body")
            if "verificação de segurança" in body_text.lower() or "captcha" in body_text.lower() or "cloudflare" in body_text.lower():
                logger.warning(f"{self.platform_name}: possível bloqueio Cloudflare/challenge detectado")
            
            # DEBUG: log first 2000 chars of body at INFO level to see structure
            logger.info(f"{self.platform_name}: body preview (2000 chars): {body_text[:2000]}")

            # Seletores para cards de projeto - tenta específicos primeiro, cai para genéricos
            card_selectors_specific = [
                # Seletores específicos de lista de resultados
                "[data-testid='projects-list'] [data-testid='project-card']",
                "[data-testid='projects-list'] .project-card",
                ".projects-list .project-card",
                ".search-results .project-card",
                ".results-container .project-card",
                "[data-cy='projects-list'] [data-cy='project-card']",
            ]
            card_selectors_generic = [
                # Seletores genéricos de card (fallback)
                "[data-testid='project-card']",
                ".project-card",
                ".job-item",
                "article",
                ".project-item",
            ]
            
            cards = []
            # Tenta seletores específicos primeiro
            for sel in card_selectors_specific:
                try:
                    await self.page.wait_for_selector(sel, timeout=3000)
                    cards = await self.page.query_selector_all(sel)
                    if cards:
                        logger.info(f"{self.platform_name}: encontrou {len(cards)} cards com seletor específico: {sel}")
                        break
                except:
                    continue
            
            # Se não achou, tenta genéricos
            if not cards:
                for sel in card_selectors_generic:
                    try:
                        await self.page.wait_for_selector(sel, timeout=3000)
                        cards = await self.page.query_selector_all(sel)
                        if cards:
                            logger.info(f"{self.platform_name}: encontrou {len(cards)} cards com seletor genérico: {sel}")
                            break
                    except:
                        continue

            if not cards:
                logger.warning(f"{self.platform_name}: nenhum card encontrado para '{term}'")
                return vagas

            # DEBUG: log first few card URLs to verify they're different
            for i, card in enumerate(cards[:5]):
                try:
                    titulo_el = await card.query_selector("a[href*='/project/']")
                    if titulo_el:
                        url = await titulo_el.get_attribute("href")
                        if url and not url.startswith("http"):
                            url = f"https://www.99freelas.com.br{url}"
                        logger.debug(f"  Card {i+1} URL: {url}")
                except:
                    pass

            for card in cards[:30]:
                try:
                    # Título e URL
                    titulo_el = await card.query_selector("a[href*='/project/'], h3 a, h2 a, .title a, [data-testid='title']")
                    titulo = await titulo_el.inner_text() if titulo_el else "Sem titulo"
                    url = await titulo_el.get_attribute("href") if titulo_el else ""
                    if url and not url.startswith("http"):
                        url = f"https://www.99freelas.com.br{url}"

                    # Filtra ruído: página de criar projeto, títulos genéricos
                    if not url or '/project/' not in url or '/project/new' in url:
                        continue
                    if titulo.strip().lower() in ["publique um projeto. é grátis.", "publique um projeto", "novo projeto"]:
                        continue

                    # Descrição
                    desc_el = await card.query_selector("[data-testid='description'], .description, .project-description, p, .text")
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
                    logger.debug(f"Erro parse card {self.platform_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"{self.platform_name}: erro ao buscar '{term}': {e}")

        return vagas