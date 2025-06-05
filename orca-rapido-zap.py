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

st.title("")  # Remove o título básico antigo

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

# Coleta informações principais do kit
codigo_kit = str(kit.get('CODIGO')).strip()
valor_kit = float(kit.get('A VISTA', 0))
peso_kit = float(kit.get('PESO UND', 0))
link_kit = kit.get('LINK_KIT', '')

# Dados do cliente e desconto
nome_cliente = st.text_input("Nome do cliente")
desc_aplicado = st.slider("Desconto aplicado (%)", 0, 12, 0)

valor_com_desc = valor_kit * (1 - desc_aplicado/100)

# Frete
distancia_total = st.number_input(
    "Distância total (em km) da franquia até o local da obra:",
    min_value=0, value=0, step=1
)
valor_frete = 1129 * (peso_kit / 1000)
if distancia_total > 200:
    km_excedente = distancia_total - 200
    valor_frete_adicional = km_excedente * 5.5
else:
    valor_frete_adicional = 0.0
f_total = valor_frete + valor_frete_adicional
total_com_frete = valor_com_desc + f_total

# Estimativa casa pronta
padrao_aframe = re.compile(r"a[-\s]?frame", re.IGNORECASE)
if padrao_aframe.search(kit_selecionado):
    estimativa_casa_pronta = valor_kit * 1.85
else:
    estimativa_casa_pronta = valor_kit * 1.90

# Formatação de moeda
def fmoeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# === Busca da planta baixa na pasta imagens ===
extensoes = [".jpg", ".png", ".jpeg"]
plantas_encontradas = []

# Planta principal: planta-XXX
for ext in extensoes:
    path1 = os.path.join("imagens", f"planta-{codigo_kit}{ext}")
    if os.path.exists(path1):
        plantas_encontradas.append(("Principal", path1))
        break

# Planta opcional: planta1-XXX
for ext in extensoes:
    path2 = os.path.join("imagens", f"planta1-{codigo_kit}{ext}")
    if os.path.exists(path2):
        plantas_encontradas.append(("Opção 2", path2))
        break

st.markdown("### Planta Baixa do Kit (para download)")
if plantas_encontradas:
    for label, img_path in plantas_encontradas:
        with open(img_path, "rb") as fimg:
            st.download_button(
                label=f"📥 Baixar Planta Baixa ({label})",
                data=fimg,
                file_name=os.path.basename(img_path),
                mime="image/jpeg" if img_path.endswith(".jpg") or img_path.endswith(".jpeg") else "image/png"
            )
else:
    st.warning("⚠️ Planta baixa não encontrada para esse kit.")

# Geração da mensagem
if st.button("Gerar Mensagem de Proposta para WhatsApp"):
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    mensagem = f"""*Proposta Comercial MCPF Bahia*
Data da Proposta: *{data_hoje}*
Cliente: *{nome_cliente}*
________________________________________
🏠 *MODELO SELECIONADO E VALORES*
• *Modelo do Kit:* {kit_selecionado}
• *Valor do Kit:* {fmoeda(valor_kit)}
• *Desconto Aplicado:* {desc_aplicado} %
• *Valor com Desconto:* {fmoeda(valor_com_desc)}
• *Valor do Frete:* {fmoeda(valor_frete)} / *Frete Adicional:* {fmoeda(valor_frete_adicional)} / *Total Frete* {fmoeda(f_total)}
• *Total com Frete:* {fmoeda(total_com_frete)}
*O Frete deverá ser pago diretamente à transportadora em até 48hs antes do embarque.* 
• *Estimativa Casa Pronta:* {fmoeda(estimativa_casa_pronta)}
________________________________________
✅ *O QUE ESTÁ INCLUSO NO KIT*
Estrutura completa em madeira Pinus autoclavada
Paredes, forros e estrutura do telhado
Portas e janelas padrão do projeto
Ripas, canaletas, rodapés, molduras, ferragens
*Manual completo de montagem e suporte técnico da equipe de engenheiros* 
Você pode contratar um carpinteiro local (opção mais econômica), ou um parceiro indicado. Se preferir, consulte também a opção *Chave na Mão*, com a casa pronta no local.
________________________________________
ℹ️ *OBSERVAÇÕES IMPORTANTES*
*Portas personalizadas, telhas, stain, vidros e mão de obra NÃO estão inclusos no kit de madeiramento.*
Prazo de entrega estimado: 30 a 60 dias após assinatura do contrato e confirmação do pagamento. 

OBS: Voce pode contratar um carpinteiro local ou utilizar um de nossos parceiros. Essa opcao costuma ser mais economica, pois evita custos com deslocamentos tecnicos e visitas a obra. Mas, se preferir mais comodidade, oferecemos tambem a opcao *CHAVE NA MAO* com a casa entregue pronta no local. Consulte as condicoes dessa modalidade. 

*Garantia de 15 anos contra pragas e apodrecimento da madeira*
*Proposta válida por 7 dias corridos.*
________________________________________
🔗 *LINK DO KIT*
{link_kit}
________________________________________
"""
    if plantas_encontradas:
        mensagem += "\n📐 PLANTA BAIXA DO KIT: disponível para download junto com a proposta.\n"

    st.markdown("### 📝 Copie e envie para o WhatsApp:")
    st.text_area("Mensagem pronta:", value=mensagem, height=400)

    # Link para WhatsApp Web com mensagem já preenchida
    st.markdown("---")
    url_whatsapp = f"https://api.whatsapp.com/send?text={quote(mensagem)}"
    st.markdown(f"[👉 Enviar mensagem via WhatsApp Web]({url_whatsapp})", unsafe_allow_html=True)
    st.info("Clique para abrir o WhatsApp Web com a mensagem pronta. Basta colar o número do cliente e enviar.")
