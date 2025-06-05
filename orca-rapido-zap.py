import streamlit as st
import pandas as pd
from datetime import datetime
from urllib.parse import quote
import re
import os

st.set_page_config(page_title="Orçamento WhatsApp MCPF", layout="centered")

st.markdown("""
    <div style="background: linear-gradient(90deg,#ffe066,#ffd60a,#e9c46a);
                padding: 18px 0;
                border-radius: 12px;
                margin-bottom: 20px;
                box-shadow: 0 4px 16px #00000009;
                text-align: center;">
        <span style="font-size:2.1rem; font-weight: bold; color:#473d0f; letter-spacing:1px;">
            MCPF-BAHIA | ORÇAMENTO RÁPIDO WHATSAPP
        </span>
        <br>
        <span style="font-size:1.05rem; color:#7d6f29;">
            Gere, baixe e envie sua proposta comercial personalizada em poucos cliques!
        </span>
    </div>
""", unsafe_allow_html=True)

# === Carrega planilha ===
df = pd.read_excel("kits.xlsx")

# === Busca do kit ===
busca = st.text_input("Digite parte do nome do kit:")
kits_filtrados = df[df['DESCRICAO'].str.contains(busca, case=False, na=False)]

if len(kits_filtrados) == 0:
    st.info("Digite parte do nome do kit para buscar.")
    st.stop()

kit_selecionado = st.selectbox("Selecione um kit:", kits_filtrados['DESCRICAO'])
kit = kits_filtrados[kits_filtrados['DESCRICAO'] == kit_selecionado].iloc[0]

# Coleta informações principais
codigo_kit = str(kit.get('CODIGO')).strip()
valor_kit = float(kit.get('A VISTA', 0))
peso_kit = float(kit.get('PESO UND', 0))
link_kit = kit.get('LINK_KIT', '')

# Dados do cliente
nome_cliente = st.text_input("Nome do cliente")
desc_aplicado = st.slider("Desconto aplicado (%)", 0, 12, 0)
valor_com_desc = valor_kit * (1 - desc_aplicado / 100)

# Frete
distancia_total = st.number_input(
    "Distância total (em km) da franquia até o local da obra:",
    min_value=0, value=0, step=1
)
valor_frete = 1129 * (peso_kit / 1000)
valor_frete_adicional = (distancia_total - 200) * 5.5 if distancia_total > 200 else 0.0
f_total = valor_frete + valor_frete_adicional
total_com_frete = valor_com_desc + f_total

# Estimativa casa pronta
padrao_aframe = re.compile(r"a[-\s]?frame", re.IGNORECASE)
estimativa_casa_pronta = valor_kit * (1.85 if padrao_aframe.search(kit_selecionado) else 1.90)

# Formatação de moeda
def fmoeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Busca planta baixa
extensoes = [".jpg", ".png", ".jpeg"]
plantas_encontradas = []

for ext in extensoes:
    path1 = os.path.join("imagens", f"planta-{codigo_kit}{ext}")
    if os.path.exists(path1):
        plantas_encontradas.append(("Principal", path1))
        break

for ext in extensoes:
    path2 = os.path.join("imagens", f"planta1-{codigo_kit}{ext}")
    if os.path.exists(path2):
        plantas_encontradas.append(("Opção 2", path2))
        break

# Exibir plantas baixas
st.markdown("### 📐 Planta Baixa Disponível para Download")
if plantas_encontradas:
    for label, img_path in plantas_encontradas:
        nome_arquivo = os.path.basename(img_path)
        st.success(f"{label}: {nome_arquivo} disponível.")
        with open(img_path, "rb") as fimg:
            st.download_button(
                label=f"📥 Baixar Planta Baixa ({label})",
                data=fimg,
                file_name=nome_arquivo,
                mime="image/jpeg" if img_path.endswith(".jpg") or img_path.endswith(".jpeg") else "image/png"
            )
else:
    st.warning("⚠️ Nenhuma planta baixa encontrada para este kit no momento.")

# Geração da proposta
if st.button("Gerar Mensagem de Proposta para WhatsApp"):
    if not nome_cliente.strip():
        st.error("⚠️ Por favor, preencha o nome do cliente antes de gerar a proposta.")
        st.stop()

    data_hoje = datetime.now().strftime("%d/%m/%Y")

    mensagem = f"""*📄 PROPOSTA COMERCIAL - MCPF BAHIA*
📅 Data: *{data_hoje}*
👤 Cliente: *{nome_cliente}*

━━━━━━━━━━━━━━━━━━━━━━
🏡 *MODELO SELECIONADO*
• *Modelo*: {kit_selecionado}
• Valor do Kit: *{fmoeda(valor_kit)}*
• Desconto Aplicado: {desc_aplicado} %
• Valor com Desconto: *{fmoeda(valor_com_desc)}*

🚚 *FRETE*
• Frete Base: *{fmoeda(valor_frete)}*
• Adicional (acima de 200km): *{fmoeda(valor_frete_adicional)}*
• Total do Frete: *{fmoeda(f_total)}*
• Total com Frete: *{fmoeda(total_com_frete)}*

📌 *O frete é pago diretamente à transportadora até 48h antes do embarque.*

🔧 *Estimativa da casa pronta no local:* *{fmoeda(estimativa_casa_pronta)}*

━━━━━━━━━━━━━━━━━━━━━━
📦 *O QUE ESTÁ INCLUSO NO KIT*
✅ Estrutura completa em madeira Pinus autoclavada (resistência garantida)
✅ Paredes, forros e estrutura do telhado
✅ Portas e janelas padrão do projeto
✅ Ripas, canaletas, rodapés, molduras, ferragens
✅ Manual de montagem + suporte técnico

📘 *Montagem descomplicada:* qualquer carpinteiro experiente, mesmo que nunca tenha montado um kit nosso, conseguirá executar a montagem com facilidade.

🔧 Isso porque fornecemos um *manual detalhado, passo a passo*, além de *suporte técnico direto da nossa equipe de engenharia* durante toda a execução da obra.

⚙️ *Não quer se envolver com a obra?* Também oferecemos a opção *Chave na Mão*, com a casa entregue pronta no local. Consulte as condições dessa modalidade.

━━━━━━━━━━━━━━━━━━━━━━
📌 *INFORMAÇÕES IMPORTANTES*
• Itens não inclusos: telhas, vidros, stain, portas personalizadas e mão de obra.
• Prazo de entrega: *30 a 60 dias* após assinatura do contrato e confirmação do pagamento.
• *Garantia de 15 anos contra pragas e apodrecimento da madeira.*
• Proposta válida por *7 dias corridos*.
"""

    if plantas_encontradas:
        mensagem += "\n📐 *Planta Baixa Disponível para Download*\n"
    else:
        mensagem += "\n❌ Planta Baixa não disponível no momento.\n"

    mensagem += f"\n🔗 *Acesse o kit completo:* {link_kit}"

    st.markdown("### 📝 Copie e envie para o WhatsApp:")
    st.text_area("Mensagem pronta:", value=mensagem, height=500)

    url_whatsapp = f"https://api.whatsapp.com/send?text={quote(mensagem)}"
    st.markdown("---")
    st.markdown(f"[👉 Enviar mensagem via WhatsApp Web]({url_whatsapp})", unsafe_allow_html=True)
    st.info("Clique para abrir o WhatsApp Web com a mensagem pronta. Basta colar o número do cliente e enviar.")
