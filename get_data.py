import asyncio
import os
import re
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd
from playwright.async_api import async_playwright

@dataclass
class DataSUSExtractor:
    '''High level helper for extracting TabNet data using Playwright.

    Parameters
    ----------
    download_dir : str
        Directory where downloaded CSV files are saved. If the
        directory does not exist it will be created.
    headless : bool
        Whether to run the browser in headless mode. Default
        True.
    '''
    download_dir: str = "."
    headless: bool = True

    def __post_init__(self) -> None:
        os.makedirs(self.download_dir, exist_ok=True)

    async def _init_browser(self):
        '''Launch a Playwright Chromium browser and return context/page.'''
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=self.headless)
        context = await browser.new_context(accept_downloads=True,
                                            downloads_path=self.download_dir)
        page = await context.new_page()
        return playwright, browser, context, page

    async def fetch(self, dataset: str, start_period: str, end_period: str,
                    row: str, column: Optional[str], contents: List[str]) -> pd.DataFrame:
        '''Fetch TabNet data for a given dataset and return a DataFrame.'''
        if dataset not in {"sia", "sih"}:
            raise ValueError("dataset must be 'sia' or 'sih'")

        start_year, start_month = map(int, start_period.split("-"))
        end_year, end_month = map(int, end_period.split("-"))
        periods = []
        y, m = start_year, start_month
        while (y < end_year) or (y == end_year and m <= end_month):
            periods.append(f"{y:04d}-{m:02d}")
            m += 1
            if m > 12:
                m = 1
                y += 1

        playwright, browser, context, page = await self._init_browser()
        try:
            if dataset == "sia":
                url = "https://datasus.saude.gov.br/informacoes-de-saude-tabnet/producao-ambulatorial-sia-sus/"
            else:
                url = "https://datasus.saude.gov.br/informacoes-de-saude-tabnet/producao-hospitalar-sih-sus/"
            await page.goto(url)

            frame = page.frame(name=re.compile("iframe", re.I))
            if frame is None:
                raise RuntimeError("Could not locate data entry frame.")

            await frame.select_option("select[name='Lin']", label=row)

            if column:
                await frame.select_option("select[name='Col']", label=column)
            else:
                await frame.select_option("select[name='Col']", label=re.compile("não ativa", re.I))

            for content_label in contents:
                option = await frame.query_selector(f"select[name='Conteudo'] option[label='{content_label}']")
                if option is None:
                    raise RuntimeError(f"Content option '{content_label}' not found")
                await option.click(modifiers=["Control"])

            for period in periods:
                option = await frame.query_selector(f"select[name='Periodo'] option[label*='{period}']")
                if option:
                    await option.click(modifiers=["Control"])

            await frame.select_option("select[name='Form']", label=re.compile("ponto-e-vírgula", re.I))

            submit_button = await frame.query_selector("input[type='submit']")
            await submit_button.click()

            await page.wait_for_selector("text=Copia como .CSV")
            csv_link = await page.query_selector("text=Copia como .CSV")
            download = await csv_link.click()

            path = await download.path()
            df = pd.read_csv(path, sep=';', decimal=',', encoding='latin-1')
            return df
        finally:
            await context.close()
            await browser.close()
            await playwright.stop()

    def to_sql(self, dataframe: pd.DataFrame, table_name: str,
               sqlite_path: Optional[str] = None,
               postgres_url: Optional[str] = None,
               if_exists: str = "replace") -> None:
        '''Persist a DataFrame to SQLite or PostgreSQL.'''
        if sqlite_path:
            import sqlite3
            conn = sqlite3.connect(sqlite_path)
            dataframe.to_sql(table_name, conn, if_exists=if_exists, index=False)
            conn.commit()
            conn.close()
        if postgres_url:
            from sqlalchemy import create_engine
            engine = create_engine(postgres_url)
            with engine.begin() as conn:
                dataframe.to_sql(table_name, conn, if_exists=if_exists, index=False)

async def main_example():
    extractor = DataSUSExtractor(download_dir="./downloads")
    df_sia = await extractor.fetch(
        dataset="sia",
        start_period="2024-01",
        end_period="2024-01",
        row="Município",
        column=None,
        contents=["Qtd. Aprovada", "Valor Aprovada"]
    )
    extractor.to_sql(df_sia, table_name="sia_producao", sqlite_path="datasus.db")
    print(df_sia.head())

if __name__ == "__main__":
    asyncio.run(main_example())
