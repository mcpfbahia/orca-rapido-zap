import streamlit as st
import streamlit.components.v1 as components
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

@st.cache_data
def carregar_planilha():
    return pd.read_excel("kits.xlsx")

def fmoeda(v):
    try:
        if v is None or v == '' or (isinstance(v, float) and pd.isna(v)):
            return "Cálculo para o modelo não gerado"
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "Cálculo para o modelo não gerado"

def calcular_chave_na_mao(valor_kit):
    """
    Calcula a estimativa Chave na Mão:
    Valor do kit sem desconto multiplicado por 2.30.
    """
    if valor_kit is None or pd.isna(valor_kit):
        return None
    return valor_kit * 2.30

def gerar_mensagem(nome_cliente, kit_selecionado, valor_kit, desc_aplicado,
                   valor_com_desc, valor_frete, valor_frete_adicional,
                   f_total, total_com_frete, area_kit, estimativa_casa_pronta,
                   plantas_encontradas, link_kit):

    data_hoje = datetime.now().strftime("%d/%m/%Y")
    mensagem = f"""*📄 PROPOSTA COMERCIAL - MCPF BAHIA*
📅 Data: *{data_hoje}*
👤 Cliente: *{nome_cliente}*

━━━━━━━━━━━━━━━━━━━━━━
🏡 *MODELO SELECIONADO*
• *Modelo*: {kit_selecionado.strip()}
• Valor do Kit: *{fmoeda(valor_kit)}*
• Desconto Aplicado: {desc_aplicado}%
• 💰 Valor com Desconto: *{fmoeda(valor_com_desc)}*

💳 *CONDIÇÕES DE PAGAMENTO*

1️⃣ À vista com {desc_aplicado}% de desconto:
• Total: *{fmoeda(valor_com_desc)}*
  - Entrada (30%): *{fmoeda(valor_com_desc * 0.3)}*
  - Saldo (70%): *{fmoeda(valor_com_desc * 0.7)}* até 48h antes do embarque

2️⃣ Cartão de Crédito:
• Até 6x sem juros: *{fmoeda(valor_kit / 6)}* por parcela (valor cheio: *{fmoeda(valor_kit)}*)
• Até 18x com juros da operadora

🏠 *Estimativa de valor para Casa Pronta:* *{fmoeda(estimativa_casa_pronta)}*

🚚 *FRETE*
• Base: *{fmoeda(valor_frete)}*
• Adicional (após 200km): *{fmoeda(valor_frete_adicional)}*
• Total: *{fmoeda(f_total)}*

💰 *VALOR FINAL COM FRETE:* *{fmoeda(total_com_frete)}*

🛠️ *TEMPO ESTIMADO DE MONTAGEM:* *{int(area_kit)} dias úteis*

📌 *O frete é pago diretamente à transportadora até 48h antes do embarque.*

━━━━━━━━━━━━━━━━━━━━━━
📦 *ITENS INCLUSOS NO KIT*
✅ Estrutura completa em madeira Pinus autoclavada  
✅ Paredes, forros e estrutura do telhado  
✅ Portas e janelas padrão  
✅ Ripas, canaletas, molduras, ferragens  
✅ Manual de montagem + suporte técnico

📘 *Montagem descomplicada:*
Carpinteiros experientes, mesmo sem prática em chalés de madeira, montam com facilidade usando nosso manual técnico e suporte da engenharia.

*👷 “Ao escolher a opção de comprar o kit de madeiramento e se responsabilizando pela obra, você economiza cerca de 20% no valor total e ainda conquista liberdade para definir cada etapa e contratar a mão de obra que preferir.”*

🔧 *Quer evitar dor de cabeça com obra?*  
Temos a opção *Chave na Mão*. Consulte condições!

━━━━━━━━━━━━━━━━━━━━━━
🚫 *ITENS NÃO INCLUSOS*
• Telhas, vidros, stain, portas especiais e mão de obra

📅 *Entrega:* 30 a 60 dias úteis após assinatura e pagamento  
🛡️ *Garantia de 15 anos contra pragas e apodrecimento*

⚠️ *Proposta válida por 7 dias corridos*  
🎯 *Promoção e estoque limitados!*
"""
    if plantas_encontradas:
        mensagem += "\n📐 *Planta Baixa Disponível para Download*\n"
    else:
        mensagem += "\n❌ Planta Baixa não disponível no momento.\n"

    if link_kit and str(link_kit).strip().lower() not in ['nan', 'none', '']:
        mensagem += f"\n🔗 *Acesse o kit completo:* {link_kit}"
    else:
        mensagem += "\n❌ Link do kit não disponível."

    return mensagem

# Interface principal
df = carregar_planilha()
busca = st.text_input("Digite parte do nome do kit:")
kits_filtrados = df[df['DESCRICAO'].str.contains(busca, case=False, na=False)]
if len(kits_filtrados) == 0:
    st.info("Digite parte do nome do kit para buscar.")
    st.stop()

kit_selecionado = st.selectbox("Selecione um kit:", kits_filtrados['DESCRICAO'])
kit = kits_filtrados[kits_filtrados['DESCRICAO'] == kit_selecionado].iloc[0]

codigo_kit = str(kit.get('CODIGO')).strip()
valor_kit = float(kit.get('A VISTA', 0))
peso_kit = float(kit.get('PESO UND', 0))
area_kit = float(str(kit.get('AREA', 0)).replace(",", ".").strip())
link_kit = kit.get('LINK_KIT', '')

nome_cliente = st.text_input("Nome do cliente").strip().title()
desc_aplicado = st.slider("Desconto aplicado (%)", 0, 12, 0)
valor_com_desc = valor_kit * (1 - desc_aplicado / 100)

distancia_total = st.number_input("Distância total (em km) da franquia até o local da obra:",
                                  min_value=0, value=0, step=1)
valor_frete = 1129 * (peso_kit / 1000)
valor_frete_adicional = (distancia_total - 200) * 5.5 if distancia_total > 200 else 0.0
f_total = valor_frete + valor_frete_adicional
total_com_frete = valor_com_desc + f_total

st.markdown("### 🧾 Resumo da Proposta")
st.markdown(f"""
- 💰 **Valor com Desconto:** {fmoeda(valor_com_desc)}
- 🚚 **Frete Total:** {fmoeda(f_total)}
- 🛠️ **Tempo Estimado de Montagem:** {int(area_kit)} dias úteis
- 💵 **Total com Frete:** {fmoeda(total_com_frete)}
""")

extensoes = [".jpg", ".png", ".jpeg"]
plantas_encontradas = []
for ext in extensoes:
    path = os.path.join("imagens", f"planta-{codigo_kit}{ext}")
    if os.path.exists(path):
        plantas_encontradas.append(path)
        break
for ext in extensoes:
    path2 = os.path.join("imagens", f"planta1-{codigo_kit}{ext}")
    if os.path.exists(path2):
        plantas_encontradas.append(path2)
        break

st.markdown("### 📐 Planta Baixa")
if plantas_encontradas:
    for img_path in plantas_encontradas:
        st.image(img_path, width=300)
        with open(img_path, "rb") as fimg:
            st.download_button("📥 Baixar Planta", data=fimg, file_name=os.path.basename(img_path))
else:
    st.warning("Nenhuma planta baixa encontrada para este kit.")

if st.button("Gerar Proposta para WhatsApp"):
    if not nome_cliente:
        st.error("Preencha o nome do cliente.")
        st.stop()
    estimativa_casa_pronta = calcular_chave_na_mao(valor_kit)
    msg = gerar_mensagem(nome_cliente, kit_selecionado, valor_kit, desc_aplicado, valor_com_desc,
                         valor_frete, valor_frete_adicional, f_total, total_com_frete,
                         area_kit, estimativa_casa_pronta, plantas_encontradas, link_kit)

    st.markdown("### 📝 Mensagem para WhatsApp")
    st.text_area("Mensagem gerada:", value=msg, height=600)

    # ✅ Botão copiar funcional com feedback
    components.html(f"""
        <textarea id="mensagem_whatsapp" style="display:none;">{msg}</textarea>
        <button id="botao_copiar" onclick="copiarMensagem()"
                style="margin-top: 10px; padding: 8px 16px; background-color: #fcd34d;
                       border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">
            📋 Copiar mensagem
        </button>

        <script>
            function copiarMensagem() {{
                const texto = document.getElementById("mensagem_whatsapp").value;
                navigator.clipboard.writeText(texto).then(() => {{
                    const botao = document.getElementById("botao_copiar");
                    const textoOriginal = botao.innerText;
                    botao.innerText = "✅ Copiado!";
                    setTimeout(() => {{
                        botao.innerText = textoOriginal;
                    }}, 2000);
                }});
            }}
        </script>
    """, height=100)

    url_whatsapp = f"https://api.whatsapp.com/send?text={quote(msg)}"
    st.markdown(f"[👉 Enviar pelo WhatsApp Web]({url_whatsapp})", unsafe_allow_html=True)
