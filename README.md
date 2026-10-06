# Scraper Vagas Freelance 99freelas -> Planilha/Notion

Coleta vagas de **99freelas** focadas em Python/automacao/bots/scrapers/dashboards,
calcula score de match com seu perfil e exporta para **Excel/CSV + Notion (opcional)**.

> **Nota sobre Workana:** Workana bloqueia IPs de datacenter (Railway, Render, etc.) via Cloudflare Challenge.
> Para rodar Workana, seria necessário proxy residencial + CAPTCHA solver (custo ~R$ 300-500/mês).
> Esta versão foca no 99freelas que permite acesso público às vagas.

## Funcionalidades
- Busca pública no 99freelas (sem login necessário)
- 14 termos otimizados para perfil Python/automacao/bot/dashboard
- Score inteligente (0-100) baseado em: skills match, propostas, reputação cliente, orçamento
- Exporta Excel (com cores: verde ≥80, amarelo 60-79) + CSV
- Sync opcional para Notion (top 20 vagas score ≥60)
- Roda em ~2-4 min headless

## Stack
- Playwright (Chromium headless)
- Pandas + OpenPyXL (Excel bonito)
- Notion API (opcional)

## Configuração Local

### 1. Clone e instale
```bash
git clone https://github.com/jvng1688-byte/scraper-vagas-freelance-.git
cd scraper-vagas-freelance-
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Variáveis de ambiente (`.env`)
```env
FREELAS_EMAIL=seu_email@99freelas
FREELAS_PASSWORD=***
NOTION_TOKEN=secret_xxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> `FREELAS_EMAIL`/`PASSWORD` são opcionais (busca é pública), mas podem ajudar se o site exigir login no futuro.
> `NOTION_TOKEN`/`DATABASE_ID` são opcionais — sync só roda se configurados.

### 3. Rode
```bash
python main.py
```
Arquivos gerados: `vagas_freelance_YYYYMMDD_HHMM.xlsx` e `.csv`

## Deploy no Railway/Render (Agendado)

### Railway (Cron Job)
1. Deploy repo como "Background Worker"
2. Settings → Cron Jobs → Add: `0 */4 * * *` (a cada 4h)
3. Start Command: `python main.py`

### Render (Cron Job)
1. Crie "Cron Job" (não Web Service)
2. Build: `pip install -r requirements.txt && playwright install chromium`
3. Command: `python main.py`
4. Schedule: `0 */4 * * *` (a cada 4h)

## Extensibilidade (Modular)
Estrutura preparada para adicionar outras plataformas:
```
platforms/
├── freelas99.py    # Implementado ✅
├── workana.py      # Placeholder (requer proxy residencial)
└── linkedin.py     # Futuro
```

## Licença
MIT - Portfolio project.