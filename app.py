import streamlit as st
import pandas as pd
import time

# 1. CONFIGURAÇÕES DA PÁGINA
st.set_page_config(page_title="Value Architect Pro", page_icon="📈", layout="centered")

# 2. ESTILOS VISUAIS (CSS PERSONALIZADO)
st.markdown("""
<style>
    /* Estilização dos botões */
    div.stButton > button:first-child {
        background-color: #1E3A8A;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #2563EB;
        border: 1px solid white;
    }
    /* Caixas de destaque */
    .highlight-card {
        background-color: #F3F4F6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E3A8A;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. VARIÁVEIS DE ESTADO DO JOGO
if 'fase' not in st.session_state:
    st.session_state.fase = 1
    st.session_state.score = 100
    st.session_state.card_idx = 0
    st.session_state.wacc = 0.0
    st.session_state.ev = 0.0

# Novas Perguntas - Cenários Práticos
cenarios = [
    {
        "titulo": "Expansão Financiada",
        "texto": "O Conselho de Administração decidiu emitir €50M em obrigações a 10 anos para construir uma nova fábrica. Qual métrica NÃO sofrerá impacto (ou seja, ignora) desta entrada de dívida?",
        "opcoes": ["Apenas FCFE", "Apenas FCFF", "Ambos são impactados"],
        "correta": "Apenas FCFF",
        "explicacao": "Correto! O FCFF (Free Cash Flow to Firm) é o fluxo de caixa disponível para todos os investidores, medido antes do serviço da dívida."
    },
    {
        "titulo": "Pressão de Fornecedores",
        "texto": "Para garantir matéria-prima, a empresa teve de pagar os fornecedores a pronto, aumentando drasticamente a necessidade de Capital de Giro (NWC). Quem sente este impacto no bolso?",
        "opcoes": ["Apenas FCFE", "Apenas FCFF", "Ambos são impactados"],
        "correta": "Ambos são impactados",
        "explicacao": "Correto! A variação do capital de giro (Working Capital) é deduzida logo no início, impactando a geração de caixa para toda a estrutura (Firm e Equity)."
    },
    {
        "titulo": "Amortização Surpresa",
        "texto": "Com o excesso de caixa do trimestre passado, o CEO decidiu antecipar a amortização de €20M do empréstimo bancário. Qual métrica regista esta saída de dinheiro?",
        "opcoes": ["Apenas FCFE", "Apenas FCFF", "Ambos são impactados"],
        "correta": "Apenas FCFE",
        "explicacao": "Excelente! O FCFE subtrai o pagamento do principal da dívida, enquanto o FCFF ignora movimentos de amortização."
    }
]

# CABEÇALHO DO JOGO
st.title("📈 Value Architect: Executive Edition")
st.markdown("Bem-vindo ao simulador. Tome as rédeas financeiras, supere a Due Diligence e maximize o *Enterprise Value* da empresa.")
st.progress(st.session_state.fase / 4)

# ==========================================
# FASE 1: DUE DILIGENCE (FLUXOS DE CAIXA)
# ==========================================
if st.session_state.fase == 1:
    st.header("Fase 1: Due Diligence")
    st.caption("A sua Reputação no Mercado: " + "⭐" * (st.session_state.score // 20))
    
    if st.session_state.card_idx < len(cenarios):
        cenario_atual = cenarios[st.session_state.card_idx]
        
        st.markdown(f"""
        <div class="highlight-card">
            <h4>📁 Caso {st.session_state.card_idx + 1}: {cenario_atual['titulo']}</h4>
            <p>{cenario_atual['texto']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for i, opcao in enumerate(cenario_atual['opcoes']):
            if cols[i].button(opcao, key=f"btn_{i}"):
                if opcao == cenario_atual['correta']:
                    st.success(cenario_atual['explicacao'])
                    time.sleep(2.5) # Pausa dramática para ler a explicação
                else:
                    st.error(f"Incorreto! A resposta certa era '{cenario_atual['correta']}'. O mercado penalizou a sua empresa.")
                    st.session_state.score -= 20
                    time.sleep(2.5)
                
                st.session_state.card_idx += 1
                st.rerun()
    else:
        st.success("🎉 Due Diligence concluída com sucesso! Os investidores estão prontos para o próximo passo.")
        if st.button("Avançar para Estrutura de Capital ➡️"):
            st.session_state.fase = 2
            st.rerun()

# ==========================================
# FASE 2: O CUSTO DO CAPITAL (WACC)
# ==========================================
elif st.session_state.fase == 2:
    st.header("Fase 2: Calibrar a Estrutura de Capital")
    st.markdown("Ajuste a alavancagem financeira. Use a dívida a seu favor (benefício fiscal), mas cuidado com o risco de insolvência que fará os credores exigirem taxas exorbitantes.")
    
    wd = st.slider("Alavancagem: Percentagem de Dívida (Debt %)", 0, 90, 25, format="%d%%") / 100.0
    we = 1 - wd
    
    # Modelo matemático para o jogo
    tax_rate = 0.25 # IRC estimado
    kd_base = 0.05
    ke_base = 0.10
    
    # Ponto de rutura aos 45% de dívida
    risco_falencia = max(0, wd - 0.45) ** 2 * 3
    kd = kd_base + risco_falencia
    ke = ke_base + (risco_falencia * 2)
    
    wacc = (we * ke) + (wd * kd * (1 - tax_rate))
    
    # Exibição visual dos custos
    col1, col2, col3 = st.columns(3)
    col1.metric("Custo do Equity (Ke)", f"{ke*100:.1f}%")
    col2.metric("Custo da Dívida (Kd)", f"{kd*100:.1f}%")
    
    # Feedback visual do WACC
    if wacc < 0.08:
        col3.metric("WACC (Taxa de Desconto)", f"{wacc*100:.2f}%", "Excelente", delta_color="normal")
    elif wacc < 0.12:
        col3.metric("WACC (Taxa de Desconto)", f"{wacc*100:.2f}%", "Aceitável", delta_color="off")
    else:
        col3.metric("WACC (Taxa de Desconto)", f"{wacc*100:.2f}%", "Risco Elevado!", delta_color="inverse")

    # Gráfico simples
    df_chart = pd.DataFrame({"Composição do Capital": ["Equity", "Dívida"], "Peso": [we, wd]}).set_index("Composição do Capital")
    st.bar_chart(df_chart, height=150)
    
    st.info("💡 **Dica do CFO:** Encontre o ponto exato onde a barra do WACC é mais baixa possível antes de confirmar.")
    
    if st.button("Gravar Estrutura e Avançar ➡️"):
        st.session_state.wacc = wacc
        st.session_state.fase = 3
        st.rerun()

# ==========================================
# FASE 3: CRESCIMENTO VS PAYOUT
# ==========================================
elif st.session_state.fase == 3:
    st.header("Fase 3: O Motor de Crescimento (Growth)")
    st.markdown("Quanto do lucro vai distribuir aos acionistas (Dividendos) e quanto vai reter na empresa para gerar crescimento na perpetuidade (g)?")
    
    caixa_gerado = 120.0 # Valor base em milhões
    roic = 0.18 # Return on Invested Capital
    
    payout = st.slider("Política de Payout (% distribuída aos acionistas)", 0, 100, 40, format="%d%%") / 100.0
    taxa_retencao = 1 - payout
    
    # Fórmulas
    g = roic * taxa_retencao
    cash_flow_ano1 = caixa_gerado * (1 + g)
    
    c1, c2 = st.columns(2)
    c1.metric("Crescimento Perpétuo (g)", f"{g*100:.2f}%", "Impulsionado pelo ROIC")
    c2.metric("Fluxo de Caixa Est. Ano 1", f"€ {cash_flow_ano1:.1f}M")
    
    # Validação matemática (Gordon Growth Model)
    if g >= st.session_state.wacc:
        st.error("⚠️ **Parado aí!** O crescimento (g) é maior ou igual ao WACC. Isso destruiria as leis da matemática financeira (o valor tenderia ao infinito). Aumente o Payout para baixar o 'g'.")
    else:
        ev_calculado = cash_flow_ano1 / (st.session_state.wacc - g)
        st.success("Valuation matematicamente viável. Pronto para descobrir o valor da empresa?")
        
        if st.button("Finalizar e Ver o Valuation 🚀"):
            st.session_state.ev = ev_calculado
            st.session_state.fase = 4
            st.rerun()

# ==========================================
# RESULTADO FINAL
# ==========================================
elif st.session_state.fase == 4:
    st.header("🏆 Resultado do Valuation")
    
    ev = st.session_state.ev
    pontuacao = st.session_state.score
    
    st.markdown(f"""
    <div style='text-align: center; padding: 30px; background-color: #1E3A8A; color: white; border-radius: 15px;'>
        <h2>Enterprise Value Final</h2>
        <h1 style='color: #FBBF24; font-size: 3em;'>€ {ev:,.1f} Milhões</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("O seu Perfil Profissional:")
    
    if ev < 800:
        st.error("📉 **Analista Júnior:** Destruiu valor. O WACC ficou demasiado alto ou reteve pouco caixa para suportar o crescimento.")
    elif ev < 1500:
        st.warning("📊 **Diretor Financeiro:** Uma empresa sólida, rentável, mas conservadora. Faltou um pouco de otimização de dívida.")
    else:
        st.balloons()
        st.success("🦄 **Mestre do Valuation (Unicórnio):** Estrutura de capital perfeita. Equilibrou crescimento e risco de forma sublime!")
        
    st.info(f"O seu nível de precisão teórica na Fase 1 foi de {pontuacao}%.")

    if st.button("🔄 Refazer a Simulação"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
