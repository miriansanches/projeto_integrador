import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="🌬️ Qualidade do Ar e Saúde",
    page_icon="🫁",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .main {
        font-family: 'Poppins', sans-serif;
    }
    
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        color: white;
        text-align: center;
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .info-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border-left: 5px solid #667eea;
    }
    
    .health-alert {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ff6b6b;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .health-good {
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
        border-left-color: #4ecdc4;
    }
    
    .health-moderate {
        background: linear-gradient(135deg, #ffd3a5 0%, #fd9853 100%);
        border-left-color: #ff9f43;
    }
    
    .health-bad {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        border-left-color: #ff6b6b;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .css-1lcbmhc {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .fade-in {
        animation: fadeIn 1s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chart-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)
import mysql.connector
import pandas as pd
import streamlit as st

def conexao(query):
    try:
        con = mysql.connector.connect(
            host="projetointegrador-grupo2.mysql.database.azure.com",
            port="3306",
            user="projeto2",
            password="senai%40134",
            database="db_sensor",
            ssl_ca="DigiCertGlobalRootG2.crt.pem"  # Caminho para o certificado
        )
        df = pd.read_sql(query, con)
        con.close()
        return df
    except Exception as e:
        st.error(f"Erro na conexão com o banco: {e}")
        return pd.DataFrame()


def classificar_qualidade_ar(co2, poeira1, poeira2):
    if co2 < 400 and poeira1 < 12 and poeira2 < 35:
        return "Boa", "🟢", "health-good"
    elif co2 < 1000 and poeira1 < 35 and poeira2 < 75:
        return "Moderada", "🟡", "health-moderate"
    else:
        return "Ruim", "🔴", "health-bad"

def obter_recomendacoes(qualidade):
    recomendacoes = {
        "Boa": [
            "✅ Ideal para atividades ao ar livre",
            "✅ Exercícios físicos recomendados",
            "✅ Janelas podem permanecer abertas",
            "✅ Baixo risco para grupos sensíveis"
        ],
        "Moderada": [
            "⚠️ Grupos sensíveis devem limitar atividades prolongadas ao ar livre",
            "⚠️ Use máscara em ambientes muito poluídos",
            "⚠️ Mantenha ambientes internos bem ventilados",
            "⚠️ Hidrate-se adequadamente"
        ],
        "Ruim": [
            "🚨 Evite atividades ao ar livre",
            "🚨 Use purificadores de ar em ambientes fechados",
            "🚨 Mantenha janelas fechadas",
            "🚨 Procure atendimento médico se sentir desconforto respiratório"
        ]
    }
    return recomendacoes.get(qualidade, [])

st.markdown('<h1 class="main-title">🌬️ Como os Componentes do Ar Influenciam na Saúde Humana 🫁</h1>', unsafe_allow_html=True)

st.sidebar.markdown("## 🎛️ Painel de Controle")
st.sidebar.markdown("---")

opcao = st.sidebar.selectbox(
    "📋 Selecione uma seção:",
    ["🏠 Menu Principal", "📊 Gráficos", "ℹ️ Sobre", "💡 Insights"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 Atualização de Dados")
if st.sidebar.button("🔄 Atualizar Dashboard"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Filtros de Data")
data_inicio = st.sidebar.date_input("Data Início", datetime.now() - timedelta(days=7))
data_fim = st.sidebar.date_input("Data Fim", datetime.now())

if opcao == "🏠 Menu Principal":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    query_recente = """
    SELECT * FROM tb_condicao_ambiental 
    ORDER BY data_hora DESC 
    LIMIT 1
    """
    dados_recentes = conexao(query_recente)
    
    if not dados_recentes.empty:
        ultimo_registro = dados_recentes.iloc[0]
        
        qualidade, emoji, classe_css = classificar_qualidade_ar(
            ultimo_registro['co2'], 
            ultimo_registro['poeira1'], 
            ultimo_registro['poeira2']
        )
        
        st.markdown(f"""
        <div class="health-alert {classe_css}">
            <h2>{emoji} Status Atual da Qualidade do Ar: {qualidade}</h2>
            <p><strong>Última atualização:</strong> {ultimo_registro['data_hora']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌡️ Temperatura</h3>
                <h2>{ultimo_registro['temperatura']:.1f}°C</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💨 CO₂</h3>
                <h2>{ultimo_registro['co2']:.0f} ppm</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💧 Umidade</h3>
                <h2>{ultimo_registro['umidade']:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌫️ Poeira PM2.5</h3>
                <h2>{ultimo_registro['poeira2']:.1f} μg/m³</h2>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("## 🏥 Recomendações de Saúde")
        recomendacoes = obter_recomendacoes(qualidade)
        
        for rec in recomendacoes:
            st.markdown(f"""
            <div class="info-card">
                <p style="margin: 0; font-size: 1.1rem;">{rec}</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Nenhum dado encontrado no banco de dados.")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif opcao == "📊 Gráficos":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("## 📈 Análise Visual dos Dados Ambientais")
    
    query_periodo = f"""
    SELECT * FROM tb_condicao_ambiental 
    WHERE DATE(data_hora) BETWEEN '{data_inicio}' AND '{data_fim}'
    ORDER BY data_hora
    """
    dados_periodo = conexao(query_periodo)
    
    if not dados_periodo.empty:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🕒 Evolução Temporal dos Parâmetros")
        
        fig_linha = make_subplots(
            rows=2, cols=2,
            subplot_titles=('🌡️ Temperatura (°C)', '💨 CO₂ (ppm)', '💧 Umidade (%)', '🌫️ Poeira PM2.5 (μg/m³³)'),
            vertical_spacing=0.1
        )
        
        fig_linha.add_trace(
            go.Scatter(x=dados_periodo['data_hora'], y=dados_periodo['temperatura'], 
                      name='Temperatura', line=dict(color='#ff6b6b')),
            row=1, col=1
        )
        
        fig_linha.add_trace(
            go.Scatter(x=dados_periodo['data_hora'], y=dados_periodo['co2'], 
                      name='CO₂', line=dict(color='#4ecdc4')),
            row=1, col=2
        )
        
        fig_linha.add_trace(
            go.Scatter(x=dados_periodo['data_hora'], y=dados_periodo['umidade'], 
                      name='Umidade', line=dict(color='#45b7d1')),
            row=2, col=1
        )
        
        fig_linha.add_trace(
            go.Scatter(x=dados_periodo['data_hora'], y=dados_periodo['poeira2'], 
                      name='Poeira PM2.5', line=dict(color='#96ceb4')),
            row=2, col=2
        )
        
        fig_linha.update_layout(height=600, showlegend=False, title_text="Monitoramento Contínuo da Qualidade do Ar")
        st.plotly_chart(fig_linha, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🔗 Matriz de Correlação entre Parâmetros")
        
        colunas_numericas = ['temperatura', 'umidade', 'pressao', 'co2', 'poeira1', 'poeira2']
        correlacao = dados_periodo[colunas_numericas].corr()
        
        fig_corr = px.imshow(
            correlacao,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdYlBu_r',
            title="Correlação entre Variáveis Ambientais"
        )
        st.plotly_chart(fig_corr, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Distribuição dos Parâmetros de Qualidade do Ar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist_co2 = px.histogram(
                dados_periodo, x='co2', 
                title='Distribuição de CO₂',
                color_discrete_sequence=['#667eea']
            )
            st.plotly_chart(fig_hist_co2, use_container_width=True)
        
        with col2:
            fig_hist_poeira = px.histogram(
                dados_periodo, x='poeira2', 
                title='Distribuição de Poeira PM2.5',
                color_discrete_sequence=['#764ba2']
            )
            st.plotly_chart(fig_hist_poeira, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🥧 Distribuição da Qualidade do Ar no Período")
        
        dados_periodo['qualidade'] = dados_periodo.apply(
            lambda row: classificar_qualidade_ar(row['co2'], row['poeira1'], row['poeira2'])[0], 
            axis=1
        )
        
        contagem_qualidade = dados_periodo['qualidade'].value_counts()
        
        fig_pizza = px.pie(
            values=contagem_qualidade.values,
            names=contagem_qualidade.index,
            title="Proporção de Dias por Qualidade do Ar",
            color_discrete_map={'Boa': '#4ecdc4', 'Moderada': '#ff9f43', 'Ruim': '#ff6b6b'}
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    else:
        st.warning("⚠️ Nenhum dado encontrado para o período selecionado.")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif opcao == "ℹ️ Sobre":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("## 📚 Sobre o Projeto")
    
    st.markdown("""
    <div class="info-card">
        <h3>🎯 Objetivo do Projeto</h3>
        <p>Este dashboard foi desenvolvido para monitorar e analisar como os componentes do ar influenciam na saúde humana. 
        Através de sensores IoT, coletamos dados em tempo real sobre a qualidade do ar e fornecemos insights valiosos 
        para a tomada de decisões relacionadas à saúde pública.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h3>🔬 Parâmetros Monitorados</h3>
        <ul>
            <li><strong>🌡️ Temperatura:</strong> Influencia o conforto térmico e pode afetar a qualidade do ar</li>
            <li><strong>💧 Umidade:</strong> Níveis inadequados podem favorecer fungos e ácaros</li>
            <li><strong>💨 CO₂:</strong> Indicador de ventilação e qualidade do ar interno</li>
            <li><strong>🌫️ Material Particulado (PM1.0 e PM2.5):</strong> Partículas que podem penetrar nos pulmões</li>
            <li><strong>📏 Pressão Atmosférica:</strong> Pode influenciar condições respiratórias</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h3>🏥 Impactos na Saúde</h3>
        <p><strong>Qualidade do Ar Ruim pode causar:</strong></p>
        <ul>
            <li>🫁 Problemas respiratórios (asma, bronquite)</li>
            <li>❤️ Doenças cardiovasculares</li>
            <li>🧠 Redução da função cognitiva</li>
            <li>👁️ Irritação nos olhos e mucosas</li>
            <li>🤧 Alergias e rinites</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h3>🛡️ Grupos de Risco</h3>
        <ul>
            <li>👶 Crianças e bebês</li>
            <li>👴 Idosos</li>
            <li>🫁 Pessoas com doenças respiratórias</li>
            <li>❤️ Portadores de doenças cardíacas</li>
            <li>🤰 Gestantes</li>
            <li>🏃 Atletas e praticantes de atividades ao ar livre</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h3>🔧 Tecnologias Utilizadas</h3>
        <ul>
            <li>🐍 Python & Streamlit para o dashboard</li>
            <li>🗄️ MySQL para armazenamento de dados</li>
            <li>📊 Plotly para visualizações interativas</li>
            <li>🌐 MQTT para comunicação IoT</li>
            <li>📡 Sensores ambientais para coleta de dados</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif opcao == "💡 Insights":
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.markdown("## 🧠 Insights e Análises Avançadas")
    
    query_insights = """
    SELECT * FROM tb_condicao_ambiental 
    ORDER BY data_hora DESC 
    LIMIT 1000
    """
    dados_insights = conexao(query_insights)
    
    if not dados_insights.empty:
        st.markdown("### 📈 Estatísticas Gerais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            media_co2 = dados_insights['co2'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h4>💨 CO₂ Médio</h4>
                <h3>{media_co2:.0f} ppm</h3>
                <p>{'🟢 Dentro do padrão' if media_co2 < 1000 else '🔴 Acima do recomendado'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            media_temp = dados_insights['temperatura'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h4>🌡️ Temperatura Média</h4>
                <h3>{media_temp:.1f}°C</h3>
                <p>{'🟢 Confortável' if 20 <= media_temp <= 26 else '⚠️ Fora da zona de conforto'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            media_poeira = dados_insights['poeira2'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <h4>🌫️ PM2.5 Médio</h4>
                <h3>{media_poeira:.1f} μg/m³</h3>
                <p>{'🟢 Boa qualidade' if media_poeira < 12 else '🔴 Qualidade comprometida'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Análise de Tendências")
        
        dados_insights['qualidade'] = dados_insights.apply(
            lambda row: classificar_qualidade_ar(row['co2'], row['poeira1'], row['poeira2'])[0], 
            axis=1
        )
        
        qualidade_counts = dados_insights['qualidade'].value_counts()
        total_registros = len(dados_insights)
        
        st.markdown(f"""
        <div class="info-card">
            <h4>🎯 Resumo da Qualidade do Ar</h4>
            <p>📊 <strong>Total de registros analisados:</strong> {total_registros}</p>
            <p>🟢 <strong>Dias com qualidade BOA:</strong> {qualidade_counts.get('Boa', 0)} ({qualidade_counts.get('Boa', 0)/total_registros*100:.1f}%)</p>
            <p>🟡 <strong>Dias com qualidade MODERADA:</strong> {qualidade_counts.get('Moderada', 0)} ({qualidade_counts.get('Moderada', 0)/total_registros*100:.1f}%)</p>
            <p>🔴 <strong>Dias com qualidade RUIM:</strong> {qualidade_counts.get('Ruim', 0)} ({qualidade_counts.get('Ruim', 0)/total_registros*100:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔍 Insights Específicos")
        
        correlacao_co2_temp = dados_insights['co2'].corr(dados_insights['temperatura'])
        
        st.markdown(f"""
        <div class="info-card">
            <h4>🌡️💨 Relação Temperatura vs CO₂</h4>
            <p>A correlação entre temperatura e CO₂ é de <strong>{correlacao_co2_temp:.3f}</strong></p>
            <p>{'📈 Correlação positiva: temperaturas mais altas tendem a ter mais CO₂' if correlacao_co2_temp > 0.3 else 
               '📉 Correlação negativa: temperaturas mais altas tendem a ter menos CO₂' if correlacao_co2_temp < -0.3 else
               '➡️ Correlação fraca: temperatura e CO₂ não estão fortemente relacionados'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        dados_insights['hora'] = pd.to_datetime(dados_insights['data_hora']).dt.hour
        co2_por_hora = dados_insights.groupby('hora')['co2'].mean()
        hora_pior = co2_por_hora.idxmax()
        hora_melhor = co2_por_hora.idxmin()
        
        st.markdown(f"""
        <div class="info-card">
            <h4>⏰ Análise por Horário</h4>
            <p>🔴 <strong>Pior horário para qualidade do ar:</strong> {hora_pior}:00h (CO₂ médio: {co2_por_hora[hora_pior]:.0f} ppm)</p>
            <p>🟢 <strong>Melhor horário para qualidade do ar:</strong> {hora_melhor}:00h (CO₂ médio: {co2_por_hora[hora_melhor]:.0f} ppm)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💊 Recomendações Baseadas em Dados")
        
        if media_co2 > 1000:
            st.markdown("""
            <div class="health-alert health-bad">
                <h4>🚨 Alerta: Níveis Elevados de CO₂</h4>
                <p>• Melhore a ventilação dos ambientes</p>
                <p>• Considere o uso de purificadores de ar</p>
                <p>• Reduza a ocupação em espaços fechados</p>
            </div>
            """, unsafe_allow_html=True)
        
        if media_poeira > 35:
            st.markdown("""
            <div class="health-alert health-bad">
                <h4>🌫️ Alerta: Material Particulado Elevado</h4>
                <p>• Use máscaras em ambientes externos</p>
                <p>• Mantenha janelas fechadas em dias poluídos</p>
                <p>• Invista em filtros HEPA</p>
            </div>
            """, unsafe_allow_html=True)
        
        if qualidade_counts.get('Boa', 0) / total_registros > 0.7:
            st.markdown("""
            <div class="health-alert health-good">
                <h4>✅ Parabéns: Boa Qualidade do Ar</h4>
                <p>• Continue monitorando os níveis</p>
                <p>• Mantenha as práticas atuais de ventilação</p>
                <p>• Aproveite para atividades ao ar livre</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.warning("⚠️ Dados insuficientes para gerar insights.")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌱 <strong>Dashboard de Qualidade do Ar e Saúde</strong> 🌱</p>
    <p>Desenvolvido com ❤️ para promover a saúde e bem-estar através do monitoramento ambiental</p>
    <p>📊 Dados atualizados em tempo real | 🔄 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
</div>
""", unsafe_allow_html=True)
