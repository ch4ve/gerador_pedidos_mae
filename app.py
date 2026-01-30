import streamlit as st
from weasyprint import HTML
from datetime import datetime
import io
from zoneinfo import ZoneInfo
import re

# --- FUNÇÃO PARA GERAR O HTML COM CONTROLES VISUAIS ---
def gerar_html(tipo_documento, cliente, fone, itens, total_calculado, forma_pagamento, prazo_entrega, exibir_total, texto_total_customizado, observacoes):
    data_hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime('%d/%m/%Y')
    
    linhas_tabela = ""
    for desc, valor in itens:
        linhas_tabela += f"""<tr><td><div class="content">{desc}</div></td><td>R$ {valor:,.2f}</td></tr>"""
    
    # Lógica do Total Geral
    # Se "exibir_total" for False, a gente esconde a linha via CSS (ou não renderiza)
    # Se tiver "texto_customizado", a gente usa ele em vez do número formatado
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
        # Converte quebras de linha em <br> para o HTML
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
if 'itens' not in st.session_state:
    st.session_state.itens = [""] 
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

    st.subheader("Itens")
    for i in range(len(st.session_state.itens)):
        st.session_state.itens[i] = st.text_input(
            f"Item {i+1} (Use $ para separar o preço)", 
            st.session_state.itens[i], 
            key=f"item_input_{i}",
            placeholder="Ex: Cortina de Linho $ 1200.00"
        )
    
    if st.button("➕ Adicionar Item"):
        st.session_state.itens.append("")
        st.rerun()

    st.subheader("Condições")
    pagamento = st.text_input("Pagamento", "Em até 3 vezes iguais sem juros...")
    entrega = st.text_input("Prazo", "30 dias úteis")

# --- LÓGICA DE CÁLCULO (Sempre roda para atualizar a preview) ---
itens_lista = []
total_calculado = 0.0
erro_validacao = False

for item_str in st.session_state.itens:
    if not item_str.strip(): continue
    if '$' in item_str:
        partes = item_str.rsplit('$', 1)
        desc = re.sub(r'\s+', ' ', partes[0].strip())
        valor_str = partes[1].strip()
        try:
            val = float(valor_str.replace('.', '').replace(',', '.'))
            itens_lista.append((desc, val))
            total_calculado += val
        except:
            pass # Ignora erro silenciosamente na digitação
    else:
        # Se não tem cifrão, não processa o valor mas guarda a descrição
        pass

# --- COLUNA 2: AJUSTES FINOS E VISUALIZAÇÃO ---
with col2:
    st.header("2. Revisar e Baixar")
    
    # --- PAINEL DE CONTROLE AMIGÁVEL ---
    with st.expander("🛠️ Ajustes Finos (Clique para abrir)", expanded=True):
        st.caption("Use as opções abaixo para personalizar o final do documento.")
        
        c1, c2 = st.columns(2)
        # Checkbox simples para mostrar ou não o total
        exibir_total = c1.checkbox("Mostrar Valor Total?", value=True)
        
        # Campo para substituir o valor numérico por texto
        texto_total_customizado = c2.text_input(
            "Substituir Total por Texto (Opcional)", 
            placeholder="Ex: A Combinar",
            disabled=not exibir_total,
            help="Escreva aqui se quiser que apareça um texto em vez da soma matemática."
        )
        
        # Campo de observações livres
        observacoes = st.text_area("Observações / Notas Extras", height=80)

    # --- GERAR PREVIEW EM TEMPO REAL ---
    if itens_lista:
        html_preview = gerar_html(
            tipo_doc, nome_cliente, fone_cliente, itens_lista, 
            total_calculado, pagamento, entrega,
            exibir_total, texto_total_customizado, observacoes
        )
        
        # Mostra o HTML renderizado
        st.components.v1.html(html_preview, height=550, scrolling=True)
        
        # Botão de Download
        st.write("---")
        col_btn1, col_btn2 = st.columns([2,1])
        
        if col_btn1.button("✅ Tudo Certo! Gerar PDF", use_container_width=True, type="primary"):
            pdf_bytes = HTML(string=html_preview).write_pdf()
            st.session_state.pdf_bytes = pdf_bytes
            
            # Nome do arquivo
            data_str = datetime.now().strftime('%d%m%Y')
            nome_limpo = re.sub(r'[^a-zA-Z0-9]', '_', nome_cliente)
            fname = f"{tipo_doc.lower()}_{nome_limpo}_{data_str}.pdf"
            
            st.download_button(
                label="⬇️ Baixar Arquivo Agora",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True
            )
            st.balloons()
            
    else:
        st.warning("👈 Preencha os itens na esquerda para ver o resultado.")
