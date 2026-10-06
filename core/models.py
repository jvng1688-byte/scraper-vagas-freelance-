"""
Core models for freelance scrapers.
"""
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Vaga:
    """Vaga de freelance padronizada."""
    plataforma: str
    titulo: str
    descricao: str
    orcamento: str
    prazo: str
    habilidades: List[str]
    propostas: int
    cliente_avaliacao: float
    cliente_projetos: int
    cliente_pagamentos: str
    url: str
    data_coleta: str
    score: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_score(vaga: Vaga) -> float:
    """Calcula score 0-100 baseado no match com perfil Python/automacao."""
    score = 50.0
    skills_text = " ".join(vaga.habilidades).lower()
    desc_text = vaga.descricao.lower()
    full_text = f"{skills_text} {desc_text}"

    high_value = [
        "python", "automacao", "bot", "telegram", "scraping", "playwright",
        "streamlit", "fastapi", "pandas", "beautifulsoup", "selenium"
    ]
    medium_value = [
        "api", "integracao", "script", "dashboard", "planilha", "excel",
        "google sheets", "csv", "json", "sqlite", "postgresql"
    ]

    for kw in high_value:
        if kw in full_text:
            score += 8
    for kw in medium_value:
        if kw in full_text:
            score += 4

    if vaga.propostas < 10:
        score += 10
    elif vaga.propostas < 20:
        score += 5

    if vaga.cliente_avaliacao >= 4.8:
        score += 10
    elif vaga.cliente_avaliacao >= 4.5:
        score += 5

    if vaga.cliente_projetos >= 10:
        score += 5
    elif vaga.cliente_projetos >= 3:
        score += 3

    try:
        orc_num = float(vaga.orcamento.replace("R$", "").replace(".", "").replace(",", ".").strip())
        if orc_num < 300:
            score -= 20
        elif orc_num < 500:
            score -= 10
    except:
        pass

    return max(0, min(100, score))