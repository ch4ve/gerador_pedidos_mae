import streamlit as st
from weasyprint import HTML
from datetime import datetime
import io
from zoneinfo import ZoneInfo
import re

# --- FUNÇÃO PARA GERAR O HTML (ADAPTADA PARA NOVA ESTRUTURA DE DADOS) ---
def gerar_html(tipo_documento, cliente, fone, itens, total_calculado, forma_pagamento, prazo_entrega, exibir_total, texto_total_customizado, observacoes):
    data_hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime('%d/%m/%Y')
    
    linhas_tabela = ""
    # Agora 'itens' é uma lista de dicionários: [{'descricao': '...', 'valor': 10.0}, ...]
    for item in itens:
        desc = item['descricao']
        valor = item['valor']
        # Só adiciona na tabela se tiver descrição preenchida
        if desc.strip():
            linhas_tabela += f"""<tr><td><div class="content">{desc}</div></td><td>R$ {valor:,.2f}</td></tr>"""
    
    # Lógica do Total Geral
    html_total = ""
    if exibir_total:
        valor_final_display = f"R$ {total_calculado:,.2f}"
        if texto_total_customizado.strip():
            valor_final_display = texto_total_customizado
            
        html_total = f"""
        <tfoot>
            <tr class="total-geral">
                <td colspan="2">TOTAL GERAL: {valor_final_display}</td>
            </tr>
        </tfoot>
        """

    # Lógica das Observações Extras
    html_obs = ""
    if observacoes.strip():
        obs_formatada = observacoes.replace('\n', '<br>')
        html_obs = f"""
        <div class="observacoes">
            <strong>Observações:</strong><br>{obs_formatada}
        </div>
        """

    disclaimer_html = ""
    if tipo_documento == "ORÇAMENTO":
        disclaimer_html = '<div class="disclaimer">Preços sujeitos a alterações sem aviso prévio.</div>'
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8"><title>{tipo_documento}</title>
        <style>
            body {{ background-color: #FFFFFF; font-family: Arial, sans-serif; margin: 40px; font-size: 14px; color: #333; }}
            .header {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #000; padding-bottom: 10px; }}
            .header-left h3, .header-left p {{ margin: 0; }}
            .header-right {{ font-size: 28px; font-family: 'Times New Roman', Times, serif; font-style: italic; }}
            .document-type {{ text-align: center; margin: 15px 0; font-size: 18px; border-top: 2px solid #000; border-bottom: 2px solid #000; padding: 5px 0; }}
            .info-cliente {{ border: 1px solid #ccc; padding: 10px; display: flex; justify-content: space-between; }}
            .tabela-itens {{ width: 100%; border-collapse: collapse; margin-top: 20px; table-layout: fixed; }}
            .tabela-itens th, .tabela-itens td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; overflow-wrap: break-word; word-wrap: break-word; word-break: break-all; }}
            .tabela-itens th {{ background-color: #e9e9e9; }}
            .th-desc {{ width: 80%; }}
            .th-valor {{ width: 20%; }}
            .total-geral td {{ font-weight: bold; font-size: 16px; text-align: right; background-color: #f0f0f0; }}
            .condicoes-gerais {{ margin-top: 25px; border: 1px solid #ccc; padding: 15px; background-color: #f9f9f9; }}
            .condicoes-gerais p {{ margin: 5px 0; }}
            .observacoes {{ margin-top: 15px; border: 1px dashed #999; padding: 10px; background-color: #fffbe6; }}
            .disclaimer {{ text-align: right; font-style: italic; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-left"><h3>REFORMAS E RESTAURAÇÕES</h3><p>RUA MANDISSUNUNGA, 174 – VILA INAH</p><p>05619-010 – SÃO PAULO – SP</p><p>Fone: (11) 3078-2757 // (11) 97056-6942</p></div>
            <div class="header-right">Léo Martins</div>
        </div>
        <div class="document-type"><h2>{tipo_documento.upper()}</h2></div>
        <div class="info-cliente"><span><strong>Cliente:</strong> {cliente}</span><span><strong>Fone:</strong> {fone}</span><span><strong>Data:</strong> {data_hoje}</span></div>
        <table class="tabela-itens">
            <thead><tr><th class="th-desc">DESCRIÇÃO</th><th class="th-valor">VALOR TOTAL</th></tr></thead>
            <tbody>{linhas_tabela}</tbody>
            {html_total}
        </table>
        
        {html_obs}

        <div class="condicoes-gerais">
            <p><strong>Forma de Pagamento:</strong> {forma_pagamento}</p>
            <p><strong>Prazo de Entrega:</strong> {prazo_entrega}</p>
        </div>
        {disclaimer_html}
    </body>
    </html>
    """
    return html_template

# --- INTERFACE DO STREAMLIT ---
st.set_page_config(page_title="Gerador de Documentos", layout="wide")
st.title("📄 Gerador de Pedidos e Orçamentos")

# Inicialização de variáveis de sessão
# AGORA A LISTA DE ITENS É UMA LISTA DE DICIONÁRIOS
if 'itens' not in st.session_state:
    st.session_state.itens = [{"descricao": "", "valor": 0.0}] 

if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None

col1, col2 = st.columns([1, 1])

# --- COLUNA 1: DADOS BRUTOS ---
with col1:
    st.header("1. Preencher Dados")
    
    with st.container(border=True):
        tipo_doc = st.selectbox("Tipo de Documento", ["ORÇAMENTO", "PEDIDO"])
        col_cli1, col_cli2 = st.columns(2)
        nome_cliente = col_cli1.text_input("Nome do Cliente")
        fone_cliente = col_cli2.text_input("Telefone")

    st.subheader("Itens do Pedido")
    st.info("Preencha a descrição e o valor separadamente.")

    # --- LOOP DE INPUTS ATUALIZADO ---
    for i, item in enumerate(st.session_state.itens):
        # Cria duas colunas para cada linha de item
        c_desc, c_val = st.columns([4, 1.5]) # A descrição ganha mais espaço
        
        with c_desc:
            item["descricao"] = st.text_input(
                f"Descrição do Item {i+1}", 
                value=item["descricao"], 
                key=f"desc_{i}",
                placeholder="Ex: Instalação de piso laminado"
            )
        
        with c_val:
            item["valor"] = st.number_input(
                f"Valor (R$)", 
                value=item["valor"], 
                min_value=0.0, 
                step=10.0, 
                format="%.2f", 
                key=f"val_{i}"
            )
    
    # Botão para adicionar nova linha vazia
    if st.button("➕ Adicionar Novo Item"):
        st.session_state.itens.append({"descricao": "", "valor": 0.0})
        st.rerun()

    st.divider()
    st.subheader("Condições")
    pagamento = st.text_input("Pagamento", "Em até 3 vezes iguais sem juros...")
    entrega = st.text_input("Prazo", "30 dias úteis")

# --- LÓGICA DE CÁLCULO (Agora muito mais simples) ---
itens_validos = []
total_calculado = 0.0

for item in st.session_state.itens:
    # Só processamos itens que tenham alguma descrição
    if item['descricao'].strip():
        itens_validos.append(item)
        total_calculado += item['valor']

# --- COLUNA 2: AJUSTES FINOS E VISUALIZAÇÃO ---
with col2:
    st.header("2. Revisar e Baixar")
    
    with st.expander("🛠️ Ajustes Finos (Opcional)", expanded=True):
        c1, c2 = st.columns(2)
        exibir_total = c1.checkbox("Mostrar Valor Total?", value=True)
        
        texto_total_customizado = c2.text_input(
            "Substituir Total por Texto", 
            placeholder="Ex: A Combinar",
            disabled=not exibir_total
        )
        observacoes = st.text_area("Observações / Notas Extras", height=80)

    # --- GERAR PREVIEW ---
    if itens_validos:
        html_preview = gerar_html(
            tipo_doc, nome_cliente, fone_cliente, itens_validos, 
            total_calculado, pagamento, entrega,
            exibir_total, texto_total_customizado, observacoes
        )
        
        st.components.v1.html(html_preview, height=550, scrolling=True)
        
        st.write("---")
        
        if st.button("✅ Gerar PDF Final", use_container_width=True, type="primary"):
            try:
                pdf_bytes = HTML(string=html_preview).write_pdf()
                
                # Gera nome do arquivo
                data_str = datetime.now().strftime('%d%m%Y')
                nome_limpo = re.sub(r'[^a-zA-Z0-9]', '_', nome_cliente) if nome_cliente else "cliente"
                fname = f"{tipo_doc.lower()}_{nome_limpo}_{data_str}.pdf"
                
                st.download_button(
                    label="⬇️ Baixar Arquivo PDF",
                    data=pdf_bytes,
                    file_name=fname,
                    mime="application/pdf",
                    use_container_width=True
                )
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
            
    else:
        st.warning("👈 Preencha pelo menos um item (com descrição) na esquerda para ver o resultado.")
