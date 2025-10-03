import streamlit as st
from weasyprint import HTML
from datetime import datetime
import speech_recognition as sr
from streamlit_audiorecorder import audiorecorder
import io

# --- FUNÇÃO GERAR_HTML (sem alterações) ---
def gerar_html(tipo_documento, cliente, fone, itens, total_geral, forma_pagamento, prazo_entrega, validade_orcamento):
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    linhas_tabela = ""
    for desc, valor in itens:
        linhas_tabela += f"<tr><td>{desc}</td><td>R$ {valor:,.2f}</td></tr>"
    
    html_template = f"""
    <!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>{tipo_documento}</title>
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
    </style></head><body>
    <div class="header"><div class="header-left"><h3>REFORMAS E RESTAURAÇÕES</h3><p>RUA MANDISSUNUNGA, 174 – VILA INAH</p><p>05619-010 – SÃO PAULO – SP</p><p>Fone: (11) 3078-2757 // (11) 97056-6942</p></div><div class="header-right">Leo Martins</div></div>
    <div class="document-type"><h2>{tipo_documento.upper()}</h2></div>
    <div class="info-cliente"><span><strong>Cliente:</strong> {cliente}</span><span><strong>Fone:</strong> {fone}</span><span><strong>Data:</strong> {data_hoje}</span></div>
    <table class="tabela-itens"><thead><tr><th>DESCRIÇÃO</th><th>VALOR TOTAL</th></tr></thead><tbody>{linhas_tabela}<tr class="total-geral"><td colspan="2">TOTAL GERAL: R$ {total_geral:,.2f}</td></tr></tbody></table>
    <div class="condicoes-gerais"><p><strong>Forma de Pagamento:</strong> {forma_pagamento}</p><p><strong>Prazo de Entrega:</strong> {prazo_entrega}</p>{'<p><em>Orçamento válido por ' + validade_orcamento + '.</em></p>' if validade_orcamento else ''}</div>
    <div class="disclaimer">Preços sujeitos a alterações sem aviso prévio.</div>
    </body></html>
    """
    return html_template

# --- INTERFACE DO STREAMLIT ---

st.set_page_config(page_title="Gerador de Documentos", layout="wide") # Mudei para layout="wide"
st.title("📄 Gerador de Pedidos e Orçamentos")

# --- INICIALIZAÇÃO DO SESSION STATE ---
if 'preview_html' not in st.session_state:
    st.session_state.preview_html = None
    st.session_state.pdf_bytes = None
    st.session_state.file_name = None

# --- CRIAÇÃO DE COLUNAS PARA O LAYOUT ---
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Dados de Entrada")
    
    # Coleta de informações
    tipo_doc = st.selectbox("Selecione o tipo de documento", ["ORÇAMENTO", "PEDIDO"])
    nome_cliente = st.text_input("Nome do Cliente")
    fone_cliente = st.text_input("Telefone do Cliente")

    st.markdown("---")
    st.subheader("Itens do Pedido/Orçamento")
    
    itens_input = st.text_area(
        "Adicione ou edite os itens aqui. Formato: DESCRIÇÃO $ VALOR",
        height=150,
        placeholder="Item 1 - Cadeira para quarto $ 1000.00\nItem 2 - Cabeceira de cama $ 500.00"
    )

    st.markdown("---")
    st.subheader("Condições Comerciais")
    pagamento = st.text_input("Forma de Pagamento", "50% de entrada + 50% na entrega")
    entrega = st.text_input("Prazo de Entrega", "30 dias úteis")
    validade = st.text_input("Validade do Orçamento (dias/semanas)", "15 dias")

    # Botão para gerar a prévia
    if st.button("👁️ Gerar Prévia"):
        try:
            # Processar os itens (lógica movida para cá)
            itens_lista = []
            total = 0.0
            linhas = itens_input.strip().split('\n')

            if not linhas or (len(linhas) == 1 and not linhas[0]):
                st.error("A caixa de itens está vazia. Por favor, adicione um item.")
                st.stop()

            for linha in linhas:
                if not linha.strip(): continue
                if '$' in linha:
                    partes = linha.rsplit('$', 1)
                    desc = partes[0].strip()
                    if not partes[1].strip():
                        st.error(f"Erro no item '{desc}': Não há valor após o '$'.")
                        st.stop()
                    valor_texto = partes[1].strip().replace('.', '').replace(',', '.')
                    valor = float(valor_texto)
                    itens_lista.append((desc, valor))
                    total += valor
            
            if not itens_lista:
                st.error("Nenhum item válido encontrado. Verifique o formato.")
            else:
                # Gerar HTML e PDF e salvar no session_state
                html_final = gerar_html(tipo_doc, nome_cliente, fone_cliente, itens_lista, total, pagamento, entrega, validade)
                pdf_bytes = HTML(string=html_final).write_pdf()
                data_arquivo = datetime.now().strftime('%d%m%Y')
                nome_arquivo_final = f"{tipo_doc.lower()}_{nome_cliente.replace(' ', '_').lower()}_{data_arquivo}.pdf"
                
                st.session_state.preview_html = html_final
                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.file_name = nome_arquivo_final
                st.success("Prévia gerada com sucesso! Veja ao lado.")

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
            # Limpar prévia anterior em caso de erro
            st.session_state.preview_html = None


with col2:
    st.header("🔍 Pré-visualização")
    
    if st.session_state.preview_html:
        # Exibe o HTML da prévia
        st.components.v1.html(st.session_state.preview_html, height=800, scrolling=True)
        
        # Exibe o botão de download SOMENTE se a prévia foi gerada
        st.download_button(
            label="✅ Baixar PDF",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.file_name,
            mime="application/pdf"
        )
    else:
        st.info("Clique em 'Gerar Prévia' para ver o documento aqui.")
# Botão para gerar o PDF
if st.button("Gerar PDF"):
    try:
        # Processar os itens
        itens_lista = []
        total = 0.0
        linhas = itens_input.strip().split('\n')
        
        # Garantir que a lista de linhas não está vazia para evitar erros
        if not linhas or (len(linhas) == 1 and not linhas[0]):
             st.error("A caixa de itens está vazia. Por favor, adicione um item.")
             # Adicionado o st.stop() para parar a execução aqui
             st.stop()

        for linha in linhas:
            # Pular linhas que por ventura estejam vazias
            if not linha.strip():
                continue

            if '$' in linha:
                partes = linha.rsplit('$', 1)
                desc = partes[0].strip()
                
                # Checar se existe algo depois do '$'
                if not partes[1].strip():
                    st.error(f"Erro no item '{desc}': Não há valor após o '$'.")
                    st.stop() # Para a execução

                # Limpa o texto do valor para que o Python entenda corretamente
                valor_texto = partes[1].strip().replace('.', '').replace(',', '.')
                valor = float(valor_texto)
                
                itens_lista.append((desc, valor))
                total += valor
        
        if not itens_lista:
            st.error("Nenhum item válido encontrado. Verifique se usou o formato 'DESCRIÇÃO $ VALOR'.")
        else:
            html_final = gerar_html(tipo_doc, nome_cliente, fone_cliente, itens_lista, total, pagamento, entrega, validade)
            pdf_bytes = HTML(string=html_final).write_pdf()

            st.success("🎉 Documento gerado com sucesso!")
            
            # --- ALTERAÇÃO PARA O NOME DO ARQUIVO ---
            # Pega a data de hoje no formato DDMMAAAA
            data_arquivo = datetime.now().strftime('%d%m%Y')
            
            # Monta o nome do arquivo com a data
            nome_arquivo_final = f"{tipo_doc.lower()}_{nome_cliente.replace(' ', '_').lower()}_{data_arquivo}.pdf"
            
            st.download_button(
                label="Clique aqui para baixar o PDF",
                data=pdf_bytes,
                file_name=nome_arquivo_final, # Usa a nova variável
                mime="application/pdf"
            )

    except ValueError:
        st.error("Ocorreu um erro ao ler um dos valores. Verifique se todos os itens após o '$' são números válidos (ex: 1970 ou 1970,50).")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao gerar o documento: {e}")

