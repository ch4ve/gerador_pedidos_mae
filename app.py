import streamlit as st
from weasyprint import HTML
from datetime import datetime
import base64

# --- FUNÇÃO PARA GERAR O HTML ---
def gerar_html(tipo_documento, cliente, fone, itens, total_geral, forma_pagamento, prazo_entrega, validade_orcamento):
    # Pega a data atual e formata
    data_hoje = datetime.now().strftime('%d/%m/%Y')

    # Monta as linhas da tabela de itens
    linhas_tabela = ""
    for desc, valor in itens:
        linhas_tabela += f"""
        <tr>
            <td>{desc}</td>
            <td>R$ {valor:,.2f}</td>
        </tr>
        """
    
    # Template HTML do documento
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
            .tabela-itens {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .tabela-itens th, .tabela-itens td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
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
        <div class="document-type"><h2>{tipo_documento.upper()}</h2></div>
        <div class="info-cliente">
            <span><strong>Cliente:</strong> {cliente}</span>
            <span><strong>Fone:</strong> {fone}</span>
            <span><strong>Data:</strong> {data_hoje}</span>
        </div>
        <table class="tabela-itens">
            <thead>
                <tr>
                    <th>DESCRIÇÃO</th>
                    <th>VALOR TOTAL</th>
                </tr>
            </thead>
            <tbody>
                {linhas_tabela}
                <tr class="total-geral">
                    <td colspan="2">TOTAL GERAL: R$ {total_geral:,.2f}</td>
                </tr>
            </tbody>
        </table>
        <div class="condicoes-gerais">
            <p><strong>Forma de Pagamento:</strong> {forma_pagamento}</p>
            <p><strong>Prazo de Entrega:</strong> {prazo_entrega}</p>
            {'<p><em>Orçamento válido por ' + validade_orcamento + '.</em></p>' if validade_orcamento else ''}
        </div>
        <div class="disclaimer">Preços sujeitos a alterações sem aviso prévio.</div>
    </body>
    </html>
    """
    return html_template

# --- INTERFACE DO STREAMLIT ---

st.set_page_config(page_title="Gerador de Documentos", layout="centered")
st.title("📄 Gerador de Pedidos e Orçamentos")

# Coleta de informações
tipo_doc = st.selectbox("Selecione o tipo de documento", ["ORÇAMENTO", "PEDIDO"])
nome_cliente = st.text_input("Nome do Cliente")
fone_cliente = st.text_input("Telefone do Cliente")

st.markdown("---")
st.subheader("Itens do Pedido/Orçamento")

# <<< ALTERAÇÃO 1: INSTRUÇÃO PARA O USUÁRIO >>>
itens_input = st.text_area(
    "Adicione os itens, um por linha, no formato: DESCRIÇÃO $ VALOR (ex: Reforma de cadeira $ 150.50)",
    height=150,
    placeholder="Item 1 - Cadeira para quarto $ 1000.00\nItem 2 - Cabeceira de cama $ 500.00"
)

st.markdown("---")
st.subheader("Condições Comerciais")
pagamento = st.text_input("Forma de Pagamento", "50% de entrada + 50% na entrega")
entrega = st.text_input("Prazo de Entrega", "30 dias úteis")
validade = st.text_input("Validade do Orçamento (dias/semanas)", "15 dias")

# Botão para gerar o PDF
if st.button("Gerar PDF"):
    try:
        # Processar os itens
        itens_lista = []
        total = 0.0
        linhas = itens_input.strip().split('\n')
        for linha in linhas:
            # <<< ALTERAÇÃO 2: LÓGICA PARA DIVIDIR A LINHA >>>
            if '$' in linha:
                partes = linha.rsplit('$', 1) # Divide a string no '$' de trás para frente, apenas uma vez
                desc = partes[0].strip()
                valor = float(partes[1].strip())
                itens_lista.append((desc, valor))
                total += valor
        
        if not itens_lista:
            st.error("Por favor, adicione pelo menos um item no formato correto.")
        else:
            # Gerar o HTML com os dados
            html_final = gerar_html(tipo_doc, nome_cliente, fone_cliente, itens_lista, total, pagamento, entrega, validade)
            
            # Converter o HTML para PDF
            pdf_bytes = HTML(string=html_final).write_pdf()

            # Criar o botão de download
            st.success("🎉 Documento gerado com sucesso!")
            st.download_button(
                label="Clique aqui para baixar o PDF",
                data=pdf_bytes,
                file_name=f"{tipo_doc.lower()}_{nome_cliente.replace(' ', '_').lower()}.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar o documento: {e}")
        st.warning("Verifique se os valores dos itens estão corretos (use ponto para decimais, ex: 150.50).")
