import streamlit as st
from weasyprint import HTML
from datetime import datetime
import io

# --- FUNÇÃO PARA GERAR O HTML ---
# Esta função cria o corpo do documento com base nos dados fornecidos.
def gerar_html(tipo_documento, cliente, fone, itens, total_geral, forma_pagamento, prazo_entrega, validade_orcamento):
    """Gera o código HTML final do documento."""
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    
    # Monta as linhas da tabela de itens
    linhas_tabela = ""
    for desc, valor in itens:
        # Formata o valor com separador de milhar e duas casas decimais
        linhas_tabela += f"<tr><td>{desc}</td><td>R$ {valor:,.2f}</td></tr>"
    
    # Template HTML com CSS incorporado
    # Inclui o CSS para quebrar palavras longas (word-wrap: break-word)
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>{tipo_documento}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; font-size: 14px; color: #333; }}
            .header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #000; padding-bottom: 10px; }}
            .header-left h3, .header-left p {{ margin: 0; }}
            .header-right {{ font-size: 28px; font-family: 'Times New Roman', Times, serif; font-style: italic; }}
            .document-type {{ text-align: center; margin: 15px 0; font-size: 18px; border-top: 2px solid #000; border-bottom: 2px solid #000; padding: 5px 0; }}
            .info-cliente {{ border: 1px solid #ccc; padding: 10px; display: flex; justify-content: space-between; }}
            .tabela-itens {{ width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }}
            .tabela-itens th, .tabela-itens td {{ border: 1px solid #ccc; padding: 8px; text-align: left; word-wrap: break-word; overflow-wrap: break-word; }}
            .tabela-itens th {{ background-color: #e9e9e9; width: 80%; }}
            .total-geral td {{ font-weight: bold; font-size: 16px; text-align: right; }}
            .condicoes-gerais {{ margin-top: 25px; border: 1px solid #ccc; padding: 15px; background-color: #f9f9f9; }}
            .condicoes-gerais p {{ margin: 5px 0; }}
            .disclaimer {{ text-align: right; font-style: italic; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left">
                <h3>REFORMAS E RESTAURAÇÕES</h3>
                <p>RUA MANDISSUNUNGA, 174 – VILA INAH</p>
                <p>05619-010 – SÃO PAULO – SP</p>
                <p>Fone: (11) 3078-2757 // (11) 97056-6942</p>
            </div>
            <div class="header-right">Leo Martins</div>
        </div>
        <div class="document-type"><h2>{tipo_
