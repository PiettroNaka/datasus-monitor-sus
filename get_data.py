import asyncio
import os
from playwright.async_api import async_playwright

async def get_datasus_data(url, group_name, periods):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print(f"Navegando para {url}...")
        await page.goto(url)
        
        # Selecionar Linha: Município gestor (index 3 no SIA/Gestor, index 0 no SIH/Gestor)
        if group_name == "sia":
            await page.select_option('select#L', index=3) # Município gestor
        else:
            await page.select_option('select#L', index=0) # Município gestor no SIH
        
        # Selecionar Coluna: Subgrupo proced.
        options = await page.query_selector_all('select#C option')
        subgroup_val = None
        for opt in options:
            text = await opt.inner_text()
            if 'Subgrupo' in text:
                subgroup_val = await opt.get_attribute('value')
                break
        if subgroup_val:
            await page.select_option('select#C', value=subgroup_val)

        # Selecionar Conteúdo: Qtd Aprovada e Valor Aprovado
        content_options = await page.query_selector_all('select#I option')
        to_select = []
        for opt in content_options:
            text = await opt.inner_text()
            if any(x in text.lower() for x in ['quantidade', 'qtd.aprovada', 'valor']):
                to_select.append(await opt.get_attribute('value'))
        await page.select_option('select#I', value=to_select[:2])
        
        # Selecionar Períodos
        period_options = await page.query_selector_all('select#A option')
        period_texts = [await opt.inner_text() for opt in period_options]
        to_select_periods = [p for p in periods if p in period_texts]
        
        if len(to_select_periods) > 12:
            print(f"Limitando a 12 períodos para {group_name}.")
            to_select_periods = to_select_periods[:12]
            
        if not to_select_periods:
            print(f"Erro: Nenhum período disponível em {group_name}.")
            await browser.close()
            return
        await page.select_option('select#A', label=to_select_periods)
        
        # Exibir linhas zeradas
        await page.check('input#Z')
        
        # Formato: Colunas separadas por ";"
        await page.click('input[value="prn"]')
        
        print(f"Gerando dados para {group_name}...")
        async with context.expect_page() as new_page_info:
            await page.click('input[type="submit"]')
        
        new_page = await new_page_info.value
        await new_page.wait_for_load_state("networkidle", timeout=120000)
        
        try:
            content = await new_page.inner_text('pre', timeout=10000)
        except:
            content = await new_page.inner_text('body')

        path = f"/home/ubuntu/data_{group_name}.csv"
        with open(path, "w", encoding="iso-8859-1") as f:
            f.write(content)
        
        print(f"Dados salvos em {path}")
        await browser.close()

async def main():
    months = ["Jan/2026", "Dez/2025", "Nov/2025", "Out/2025", "Set/2025", "Ago/2025", "Jul/2025", "Jun/2025", "Mai/2025", "Abr/2025", "Mar/2025", "Fev/2025", "Jan/2025"]
    
    sih_url = "https://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/spgbr.def"
    sia_url = "https://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qgbr.def"
    
    # print("Iniciando extração SIH...")
    # await get_datasus_data(sih_url, "sih", months)
        
    print("Iniciando extração SIA...")
    await get_datasus_data(sia_url, "sia", months)

if __name__ == "__main__":
    asyncio.run(main())
