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
        <div class="document-type"><h2>{tipo_documento.upper()}</h2></div>
        <div class="info-cliente">
            <span><strong>Cliente:</strong> {cliente}</span>
            <span><strong>Fone:</strong> {fone}</span>
            <span><strong>Data:</strong> {data_hoje}</span>
        </div>
        <table class="tabela-itens">
            <thead><tr><th>DESCRIÇÃO</th><th>VALOR TOTAL</th></tr></thead>
            <tbody>
                {linhas_tabela}
                <tr class="total-geral"><td colspan="2">TOTAL GERAL: R$ {total_geral:,.2f}</td></tr>
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

# Configura a página para usar o layout largo
st.set_page_config(page_title="Gerador de Documentos", layout="wide")
st.title("📄 Gerador de Pedidos e Orçamentos")

# Inicializa o 'session_state' para guardar os dados da prévia
if 'preview_html' not in st.session_state:
    st.session_state.preview_html = None
    st.session_state.pdf_bytes = None
    st.session_state.file_name = None

# Divide a tela em duas colunas para melhor organização
col1, col2 = st.columns([1, 1])

# --- COLUNA DE ENTRADA DE DADOS ---
with col1:
    st.header("📝 Dados de Entrada")
    
    tipo_doc = st.selectbox("Selecione o tipo de documento", ["ORÇAMENTO", "PEDIDO"])
    nome_cliente = st.text_input("Nome do Cliente")
    fone_cliente = st.text_input("Telefone do Cliente")

    st.markdown("---")
    st.subheader("Itens do Pedido/Orçamento")
    
    itens_input = st.text_area(
        "Adicione os itens, um por linha. Formato: DESCRIÇÃO $ VALOR",
        height=200,
        placeholder="Item 1 - Cadeira de couro 2,70x1,30m $ 1.200,00\nItem 2 - Reforma de sofá $ 1970"
    )

    st.markdown("---")
    st.subheader("Condições Comerciais")
    pagamento = st.text_input("Forma de Pagamento", "50% de entrada + 50% na entrega")
    entrega = st.text_input("Prazo de Entrega", "30 dias úteis")
    validade = st.text_input("Validade do Orçamento (dias/semanas)", "15 dias")

    # Botão principal para gerar a pré-visualização
    if st.button("👁️ Gerar Prévia", use_container_width=True):
        try:
            itens_lista = []
            total = 0.0
            linhas = itens_input.strip().split('\n')

            # Validação para evitar erro com caixa de texto vazia
            if not itens_input.strip():
                st.error("A caixa de itens está vazia. Por favor, adicione um item.")
                st.stop()

            for i, linha in enumerate(linhas):
                if not linha.strip(): continue # Pula linhas em branco
                if '$' in linha:
                    partes = linha.rsplit('$', 1)
                    desc = partes[0].strip()
                    
                    if not partes[1].strip():
                        st.error(f"Erro na linha {i+1} ('{desc}'): Não há valor após o '$'.")
                        st.stop()
                    
                    # Limpeza do valor: remove pontos de milhar e troca vírgula por ponto
                    valor_texto = partes[1].strip().replace('.', '').replace(',', '.')
                    valor = float(valor_texto)
                    
                    itens_lista.append((desc, valor))
                    total += valor
                else:
                    st.error(f"Erro na linha {i+1}: Item '{linha}' não contém o separador '$'.")
                    st.stop()
            
            if not itens_lista:
                st.error("Nenhum item válido encontrado. Verifique o formato.")
            else:
                # Gera o HTML e o PDF
                html_final = gerar_html(tipo_doc, nome_cliente, fone_cliente, itens_lista, total, pagamento, entrega, validade)
                pdf_bytes = HTML(string=html_final).write_pdf()
                
                # Gera o nome do arquivo, incluindo a data
                data_arquivo = datetime.now().strftime('%d%m%Y')
                nome_arquivo_final = f"{tipo_doc.lower()}_{nome_cliente.replace(' ', '_').lower()}_{data_arquivo}.pdf"
                
                # Salva os dados no session_state para serem usados pela prévia e pelo botão de download
                st.session_state.preview_html = html_final
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.file_name = nome_arquivo_final
                st.success("Prévia gerada com sucesso! Veja ao lado.")

        except ValueError:
            st.error("Erro ao ler um valor. Verifique se todos os itens após o '$' são números válidos (ex: 1970 ou 1970,50).")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
            st.session_state.preview_html = None # Limpa a prévia em caso de erro

# --- COLUNA DE PRÉ-VISUALIZAÇÃO ---
with col2:
    st.header("🔍 Pré-visualização")
    
    if st.session_state.preview_html:
        # Mostra o documento renderizado como HTML
        st.components.v1.html(st.session_state.preview_html, height=800, scrolling=True)
        
        # O botão de download só aparece APÓS a prévia ser gerada com sucesso
        st.download_button(
            label="✅ Baixar PDF",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.file_name,
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.info("Clique em 'Gerar Prévia' para ver o documento aqui.")
