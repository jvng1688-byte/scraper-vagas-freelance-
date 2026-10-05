# Scraper Vagas Freelance -> Planilha/Notion

Coleta vagas de **Workana** e **99freelas** focadas em Python/automacao/bots/scrapers/dashboards, 
calcula score de match com seu perfil e exporta para **Excel/CSV + Notion (opcional)**.

## Funcionalidades
- Login automatico nas duas plataformas
- Busca por 14 termos otimizados para seu perfil
- Score inteligente (0-100) baseado em: skills match, propostas, reputacao cliente, orcamento
- Exporta Excel (com cores: verde >=80, amarelo 60-79) + CSV
- Sync opcional para Notion (top 20 vagas score >=60)
- Roda em ~3-5 min headless

## Stack
- Playwright (Chromium headless)
- Pandas + OpenPyXL (Excel bonito)
- Notion API (opcional)

## Configuracao Local

### 1. Clone e instale
```bash
git clone https://github.com/jvng16688/scraper-vagas-freelance.git
cd scraper-vagas-freelance
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Variaveis de ambiente (`.env`)
```env
WORKANNA_EMAIL=seu_email@workana
WORKANNA_PASSWORD=***
FREELAS_EMAIL=seu_email@99freelas
FREELAS_PASSWORD=***
NOTION_TOKEN=secret_xxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Rode
```bash
python main.py
```
Arquivos gerados: `vagas_freelance_YYYYMMDD_HHMM.xlsx` e `.csv`

## Deploy no Railway/Render (Agendado)

### Railway (Cron Job)
1. Deploy repo como "Background Worker"
2. Settings -> Cron Jobs -> Add: `0 */4 * * *` (a cada 4h)
3. Start Command: `python main.py`

### Render (Cron Job)
1. Crie "Cron Job" (nao Web Service)
2. Build: `pip install -r requirements.txt && playwright install chromium`
3. Command: `python main.py`
4. Schedule: `0 */4 * * *` (a cada 4h)

## Licenca
MIT - Portfolio project.