import json
import os
import re
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path

from playwright.sync_api import sync_playwright

URL_INICIAL = "https://portaldatransparencia.gov.br/"
PASTA_BASE = Path(__file__).resolve().parent
ARQUIVO_JSON = PASTA_BASE / "resultado_busca.json"
ARQUIVO_EVIDENCIA = PASTA_BASE / "evidencia_busca.png"


def limpar_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf or "")[:11]


def validar_cpf(cpf: str) -> bool:
    cpf = limpar_cpf(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito1 = 0 if resto == 10 else resto

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito2 = 0 if resto == 10 else resto

    return digito1 == int(cpf[9]) and digito2 == int(cpf[10])


def validar_termo(termo: str):
    termo = (termo or "").strip()
    if not termo:
        raise ValueError("Informe um nome ou CPF para a busca.")

    if re.fullmatch(r"\d{11}", termo):
        if not validar_cpf(termo):
            raise ValueError("CPF inválido. Verifique os números informados.")
        return termo

    if re.fullmatch(r"\d+", termo):
        raise ValueError("CPF inválido. Informe 11 dígitos numéricos.")

    if len(termo) < 3:
        raise ValueError("Informe pelo menos 3 caracteres para o nome.")

    if any(char.isdigit() for char in termo):
        raise ValueError("Nome inválido. Não utilize números no campo de nome.")

    return termo


def clicar_se_existir(page, seletor: str, timeout_ms: int = 5000):
    try:
        elemento = page.locator(seletor)
        if elemento.count() > 0:
            elemento.first.wait_for(state="visible", timeout=timeout_ms)
            elemento.first.click(timeout=timeout_ms)
            return True
    except Exception:
        pass
    return False


def clicar_botao_texto(page, texto: str, timeout_ms: int = 5000):
    try:
        locator = page.get_by_role("button", name=re.compile(texto, re.I))
        if locator.count() > 0:
            locator.first.wait_for(state="visible", timeout=timeout_ms)
            locator.first.click(timeout=timeout_ms)
            return True
    except Exception:
        pass
    return False


def preencher_campo_busca(page, termo: str):
    campo = page.locator('input[name="termo"][id="termo"]')
    if campo.count() > 0:
        campo.first.wait_for(state="visible", timeout=10000)
        campo.first.fill(termo)
        return True
    return False


def clicar_card_pessoas(page):
    seletores = [
        "h5:has-text('Pessoas Físicas e Jurídicas')",
        "text=Pessoas Físicas e Jurídicas",
        "div.card.card-back",
        "div:has-text('Pessoas Físicas e Jurídicas')",
        "span:has-text('Pessoas Físicas e Jurídicas')",
        "[onclick*='pessoa-fisica']",
    ]
    for seletor in seletores:
        try:
            elemento = page.locator(seletor)
            if elemento.count() > 0:
                elemento.first.wait_for(state="visible", timeout=8000)
                elemento.first.click(timeout=8000)
                return True
        except Exception:
            pass
    return False


def clicar_pesquisa(page):
    seletores = [
        'button.br-button[type="submit"][aria-label*="Enviar dados do formulário de busca" i]',
        'button[type="submit"]:has(i.fas.fa-search)',
        'button[type="submit"]',
        'button.br-button',
        'i.fas.fa-search',
        'i.fa-search',
        'button:has(i.fas.fa-search)',
        'button:has(i.fa-search)',
        '[aria-label*="buscar" i]',
        '[aria-label*="pesquisar" i]',
    ]
    for seletor in seletores:
        try:
            elemento = page.locator(seletor)
            if elemento.count() > 0:
                elemento.first.wait_for(state="visible", timeout=8000)
                try:
                    elemento.first.click(timeout=8000)
                    return True
                except Exception:
                    elemento.first.evaluate("el => el.click()")
                    return True
        except Exception:
            pass

    try:
        page.keyboard.press("Enter")
        return True
    except Exception:
        return False


def coletar_dados(page):
    resultado = None

    candidatos = [
        'a.link-busca-nome',
        'a[href*="/busca/pessoa-fisica/"]',
        'a[href*="/pessoa-fisica/"]',
        'a',
    ]

    for seletor in candidatos:
        try:
            elementos = page.locator(seletor)
            if elementos.count() > 0:
                for index in range(min(elementos.count(), 10)):
                    texto = elementos.nth(index).text_content().strip()
                    if texto and len(texto) > 3 and not texto.lower().startswith(('http', 'javascript')):
                        resultado = texto
                        break
                if resultado:
                    break
        except Exception:
            continue

    return {
        "url": page.url,
        "resultado_principal": resultado,
    }


def executar_busca(termo: str, filtro_social: bool = False):
    termo_valido = validar_termo(termo)
    termo_busca = termo_valido
    if filtro_social:
        termo_busca = f"{termo_busca} BENEFICIÁRIO DE PROGRAMA SOCIAL"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox"],
        )
        context = browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        page.set_default_timeout(30000)

        page.goto(URL_INICIAL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        clicar_se_existir(page, "#accept-minimal-btn")
        page.wait_for_timeout(1500)

        clicar_card_pessoas(page)
        page.wait_for_timeout(1500)

        clicar_botao_texto(page, "Acessar busca")
        page.wait_for_timeout(2500)

        clicar_se_existir(page, "#accept-minimal-btn")
        page.wait_for_timeout(1500)

        if not preencher_campo_busca(page, termo_busca):
            raise RuntimeError("Campo de busca não encontrado na página.")

        clicar_pesquisa(page)
        page.wait_for_timeout(5000)

        clicar_se_existir(page, 'a.link-busca-nome')
        page.wait_for_timeout(3000)

        dados = {
            "termo": termo_valido,
            "filtro_social": filtro_social,
            "status": "sucesso",
            **coletar_dados(page),
        }

        page.screenshot(path=str(ARQUIVO_EVIDENCIA), full_page=True)
        with ARQUIVO_JSON.open("w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)

        try:
            input("Automação concluída. Pressione ENTER para fechar o navegador manualmente...\n")
        except Exception:
            pass

        return dados


def abrir_interface():
    root = tk.Tk()
    root.title("Buscador Portal da Transparência")
    root.geometry("480x260")
    root.resizable(False, False)

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    ttk.Label(root, text="Busca de Pessoa Física", font=("Segoe UI", 16, "bold")).pack(pady=(18, 8))

    ttk.Label(root, text="Informe CPF ou nome:", font=("Segoe UI", 10)).pack(anchor="w", padx=24)
    termo_var = tk.StringVar()
    campo = ttk.Entry(root, textvariable=termo_var, width=40, font=("Segoe UI", 11))
    campo.pack(padx=24, pady=(4, 8), fill="x")
    campo.focus()

    filtro_var = tk.BooleanVar()
    ttk.Checkbutton(
        root,
        text="Filtrar por BENEFICIÁRIO DE PROGRAMA SOCIAL",
        variable=filtro_var,
        onvalue=True,
        offvalue=False,
    ).pack(anchor="w", padx=24, pady=(4, 10))

    status_var = tk.StringVar(value="Pronto para buscar")
    ttk.Label(root, textvariable=status_var, foreground="#2f6f4f", font=("Segoe UI", 9)).pack(pady=(4, 6))

    def iniciar_busca():
        try:
            termo = validar_termo(termo_var.get())
        except ValueError as erro:
            messagebox.showerror("Entrada inválida", str(erro))
            return

        status_var.set("Buscando...")
        root.update_idletasks()
        try:
            dados = executar_busca(termo, filtro_social=filtro_var.get())
            mensagem = f"Busca concluída com sucesso.\nResultado: {dados.get('resultado_principal') or 'Sem resultado'}"
            messagebox.showinfo("Sucesso", mensagem)
            status_var.set("Busca concluída")
        except Exception as erro:
            messagebox.showerror("Erro na automação", str(erro))
            status_var.set("Erro na busca")

    botao = ttk.Button(root, text="Buscar", command=iniciar_busca)
    botao.pack(pady=(6, 16))

    root.mainloop()


if __name__ == "__main__":
    abrir_interface()
