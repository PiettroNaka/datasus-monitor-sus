import asyncio
import os
from playwright.async_api import async_playwright

async def get_datasus_data(url, group_name, periods):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Aumentar timeout e adicionar retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Navegando para {url} (Tentativa {attempt+1})...")
                await page.goto(url, timeout=60000, wait_until="networkidle")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Erro fatal ao navegar para {url}: {e}")
                    await browser.close()
                    return
                print(f"Erro ao navegar, tentando novamente... {e}")
                await asyncio.sleep(5)
        
        # Selecionar Linha: Município
        # No SIH e SIA, 'Município' costuma ser o index 0 ou ter valor 'Município'
        try:
            await page.select_option('select#L', label='Município')
        except:
            await page.select_option('select#L', index=0)
        
        # Selecionar Coluna: Subgrupo proced.
        try:
            await page.select_option('select#C', label='Subgrupo proced.')
        except:
            # Fallback para procurar por texto parcial
            options = await page.query_selector_all('select#C option')
            for opt in options:
                text = await opt.inner_text()
                if 'Subgrupo' in text:
                    val = await opt.get_attribute('value')
                    await page.select_option('select#C', value=val)
                    break

        # Selecionar Conteúdo: Qtd Aprovada e Valor Aprovado
        # Usar label para ser mais preciso
        content_options = await page.query_selector_all('select#I option')
        to_select = []
        for opt in content_options:
            text = await opt.inner_text()
            text_lower = text.lower()
            if 'quantidade' in text_lower or 'valor' in text_lower:
                to_select.append(await opt.get_attribute('value'))
        
        if to_select:
            await page.select_option('select#I', value=to_select[:2])
        
        # Selecionar Períodos
        period_options = await page.query_selector_all('select#A option')
        available_period_texts = [await opt.inner_text() for opt in period_options]
        
        to_select_periods = [p for p in periods if p in available_period_texts]
        
        if not to_select_periods:
            print(f"Erro: Nenhum período disponível em {group_name}.")
            await browser.close()
            return
            
        print(f"Selecionando {len(to_select_periods)} períodos para {group_name}...")
        await page.select_option('select#A', label=to_select_periods)
        
        # Exibir linhas zeradas (checkbox Z)
        try:
            await page.check('input#Z')
        except:
            # Em algumas versões pode não ter id, mas tem nome
            await page.check('input[name="percorrer"]')
        
        # Formato: Colunas separadas por ";" (radio prn)
        await page.click('input[value="prn"]')
        
        print(f"Gerando dados para {group_name}...")
        # O submit abre uma nova aba/janela
        async with context.expect_page() as new_page_info:
            await page.click('input[type="submit"]')
        
        new_page = await new_page_info.value
        await new_page.wait_for_load_state("networkidle", timeout=300000)
        
        try:
            # Tentar pegar do <pre>
            content = await new_page.inner_text('pre', timeout=30000)
        except:
            # Fallback para o body todo se não achar <pre>
            content = await new_page.inner_text('body')

        path = f"/home/ubuntu/data_{group_name}.csv"
        with open(path, "w", encoding="iso-8859-1") as f:
            f.write(content)
        
        print(f"Dados salvos em {path}")
        await browser.close()

async def main():
    # Períodos de Jan/2024 a Jan/2026
    # Note: Jan/2026 pode não estar disponível ainda, o script vai pegar o que houver.
    months_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    years = [2024, 2025, 2026]
    all_periods = []
    for y in years:
        for m in months_pt:
            p = f"{m}/{y}"
            all_periods.append(p)
            if p == "Jan/2026": break
        if "Jan/2026" in all_periods: break
            
    # URLs diretas para o TabNet
    sih_url = "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/spabr.def"
    sia_url = "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qabr.def"
    
    print("Iniciando extração SIH...")
    await get_datasus_data(sih_url, "sih", all_periods)
        
    print("Iniciando extração SIA...")
    await get_datasus_data(sia_url, "sia", all_periods)

if __name__ == "__main__":
    asyncio.run(main())
