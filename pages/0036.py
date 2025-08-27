# -*- coding: utf-8 -*-
# Página individual do Sensor 0036 - Pça. Luis La Saigne x Av. Maracanã

import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from sqlalchemy import create_engine
import urllib
import folium

# Função para colorir
def get_cor(valor, sensor_id, tipo="COTA"):
    """Retorna a cor baseada no valor e tipo (COTA/ALERTA)"""
    try:
        if valor is None or pd.isna(valor):
            return "#FFFFFF"
            
        valor_float = float(str(valor).replace(',', '.'))
        
        # Parâmetros específicos para o sensor 0036
        PARAMETROS_0036 = {
            "COTA": {
                "observacao": (0, 10.85),
                "alerta": (10.86, 12.46), 
                "critico": (12.47, float('inf'))
            },
            "ALERTA": {
                "observacao": (0, 38),
                "atencao": (39, 73),
                "alerta": (74, 99),
                "critico": (100, float('inf'))
            }
        }
        
        params = PARAMETROS_0036[tipo]
        
        if tipo == "COTA":
            if valor_float >= params["critico"][0]:
                return "#FF4500"
            elif valor_float >= params["alerta"][0]:
                return "#FFA500"
            return "#1E90FF"
        
        elif tipo == "ALERTA":
            if valor_float >= params["critico"][0]:
                return "#FF4500"
            elif valor_float >= params["alerta"][0]:
                return "#FFA500"
            elif valor_float >= params["atencao"][0]:
                return "#FFD700"
            return "#1E90FF"
            
    except Exception as e:
        print(f"Erro em get_cor: {str(e)}")
        return "#FFFFFF"

# Configuração da conexão com o banco (mesma do app.py)
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.5.232.43;"             
    "DATABASE=NivelRios;"             
    "UID=user_nivel_rio;"             
    "PWD=nra2bLcpRbb03O1"             
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# Query para dados históricos do sensor específico
query_historico = """
SELECT TOP 48 * FROM dados_sensores 
    WHERE nome = '0036' 
    ORDER BY data DESC, hora_formatada DESC
"""
query_top_1 = """
    SELECT TOP 1 * FROM dados_sensores 
    WHERE nome = '0036' 
    ORDER BY data DESC, hora_formatada DESC
    """
query_total_registros = """
SELECT * FROM dados_sensores 
    WHERE nome = '0036' 
    ORDER BY data DESC, hora_formatada DESC
""" 

df_top_1 = pd.read_sql(query_top_1, engine)
df_hist = pd.read_sql(query_historico, engine)
df_toal_reg = pd.read_sql(query_total_registros, engine)
row = df_top_1.iloc[0]
total_registros = len(df_toal_reg)
status = "Online" if total_registros > 0 else "Offline"
cor = "success" if total_registros > 0 else "danger"
icone = "fas fa-check-circle" if total_registros > 0 else "fas fa-exclamation-triangle"

dados_atuais_layout = html.Div([
        dbc.Row([
            dbc.Col([
                html.H5(f"{row['distancia']} cm", className="text-light"),
                html.Small("Distância")
            ], md=3),
            dbc.Col([
                html.H5(f"{row['cota']}", 
                    style={"color": get_cor(row['cota'], "0036", "COTA")}),  # ← COR DINÂMICA,
                html.Small("Cota")
            ], md=3),
            dbc.Col([
                html.H5(f"{row['percentual_alerta']}%", 
                    style={"color": get_cor(row['percentual_alerta'], "0036", "ALERTA")}),  # ← COR DINÂMICA,
                html.Small("% Alerta")
            ], md=3),
            dbc.Col([
                html.H5(f"{row['temperatura']}°C", className="text-light"),
                html.Small("Temperatura")
            ], md=3)
        ]),
        html.Hr(),
        html.P(f"Última atualização: {row['data']} {row['hora_formatada']}", style={"fontSize": "12px", "color": "#ccc"})
    ])

status_layout = html.Div([
        html.H5([html.I(className=f"{icone} me-2"), status], className=f"text-{cor}"),
        html.P(f"Registros hoje: {total_registros}")
    ])
    
debug_layout = html.Pre(
    f"Última atualização: {datetime.now().strftime('%H:%M:%S')}\n"
    f"Status: OK - Dados carregados na inicialização da página.",
    style={"color": "green"}
)

# Prepara os DataFrames para os gráficos
df_hist['distancia_num'] = pd.to_numeric(df_hist['distancia'].astype(str).str.replace(',', '.'), errors='coerce')
df_hist['cota_num'] = pd.to_numeric(df_hist['cota'].astype(str).str.replace(',', '.'), errors='coerce')
df_hist['alerta_num'] = pd.to_numeric(df_hist['percentual_alerta'].astype(str).str.replace(',', '.'), errors='coerce')

# Gera as figuras dos gráficos
fig_dist = px.line(df_hist.sort_values(['data', 'hora_formatada']), x='hora_formatada', y='distancia_num', markers=True, color_discrete_sequence=["#0199ff"], line_shape='spline') # color_discrete_sequence - define a cor da linha na criação do gráfico
fig_dist.update_layout(xaxis=dict(showgrid=False), 
                       yaxis=dict(showgrid=False,range=[0, 323]), # Altera o tamanho do eixo Y
                       plot_bgcolor='rgba(0,0,0,0)', 
                       paper_bgcolor='rgba(0,0,0,0)', 
                       font_color='white', 
                       xaxis_title="Hora", 
                       yaxis_title="Distância (cm)",
                    #    height=300 # Altura geral do gráfico
)
fig_dist.update_traces(#line=dict(color="yellow") # Define a cor da linha, após a criação do gráfico
                       line=dict(width=5),        # Define o tamanho da linha do gráfico
                       marker=dict(size=10)       # Define o tamanho do marcador                
) 

# Valores para as % de atenção, alerta e crítico do gráfico de linhas
atencao = 161
alerta  = 242
critico = 323

atencao_porc = atencao/323*100
alerta_porc  = alerta/323*100
critico_porc = critico/323*100

print("** Sensor 0036 **")
print("atenção:", atencao_porc)
print("alerta:", alerta_porc)
print("crítico:", critico_porc)

# Adiciona as linhas com valores fixos no gráfico de Histórico de Distância
fig_dist.add_hline(y=atencao, line_color="yellow", line_dash="dash", annotation_text="Atenção (49.84%)", annotation_position="top right")
fig_dist.add_hline(y=alerta, line_color="orange", line_dash="dash", annotation_text="Alerta (74.92%)", annotation_position="top right")
fig_dist.add_hline(y=critico, line_color="red", line_dash="dash", annotation_text="Crítico (100%)", annotation_position="top right")


# fig_cota = px.line(df_hist.sort_values(['data', 'hora_formatada']), x='hora_formatada', y=['cota_num', 'alerta_num'], markers=True)
# fig_cota.update_layout(xaxis=dict(showgrid=False), 
#                        yaxis=dict(showgrid=False,range=[0, 30]),
#                        plot_bgcolor='rgba(0,0,0,0)', 
#                        paper_bgcolor='rgba(0,0,0,0)', 
#                        font_color='white', 
#                        xaxis_title="Hora", 
#                        yaxis_title="Valores",
#                        height=300 # Altura geral do gráfico
# )

# # Adiciona as linhas com valores fixos no gráfico de cota
# fig_cota.add_hline(y=161, line_color="yellow", line_dash="dash", annotation_text="Atenção", annotation_position="top left")
# fig_cota.add_hline(y=242, line_color="orange", line_dash="dash", annotation_text="Alerta", annotation_position="top left")
# fig_cota.add_hline(y=323, line_color="red", line_dash="dash", annotation_text="Crítico", annotation_position="top left")


# Cria o mapa de geolocalização do sensor
lat, lon = -22.9235, -43.25

# Mapa com tiles Stamen Terrain + atribuição correta
m = folium.Map(
    location=[lat, lon],
    zoom_start=25,
    # titles='cartodb positron'
    tiles='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
)

# Marcador estilizado
folium.Marker(
    location=[lat, lon],
    popup=folium.Popup("<b>Sensor 0036</b><br>Status: OK", max_width=300),
    tooltip="Clique aqui",
    # icon=folium.Icon(color='red', icon='facetime-video') # Site com os ícones: https://www.w3schools.com/icons/bootstrap_icons_glyphicons.asp
    icon=folium.Icon(color='black', icon='fas fa-broadcast-tower', prefix='fa') # Usado o prefix='fa', para informar que o ícone é do fontawesome
).add_to(m)

# Exibir no notebook (funciona se o renderizador suportar)
# display(m)

# Ou abrir no navegador
m.save("mapa_sensor_0036.html") # Salva o mapa como arquivo html
# webbrowser.open("mapa_sensor_0036.html")



# Layout da página do sensor
layout = html.Div([
    # Cabeçalho da página
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H2(
                    "Sensor 0036 - Rio Joana x Barão de São Francisco",
                    style={"color": "#f8f9fa", 
                           "marginBottom": "30px",
                           "textAlign": "center",
                           "textShadow": "1px 1px 2px rgba(0,0,0,0.5)"}
                ),
                dbc.Button(
                    [html.I(className="fas fa-arrow-left me-2"), "Voltar ao Dashboard"],
                    href="/",
                    # color="secondary",
                    color="info",
                    className="mb-3"
                )                
            ])
        ])
    ]),
    
    # Linha com cards de informações atuais
        dbc.Container([    
            dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H4("Dados Atuais", className="text-white mb-0"),
                                style={"backgroundColor": "#20497e"}
                            ),
                            dbc.CardBody(dados_atuais_layout, style={"backgroundColor": "#2a5a8f", "color": "white"})
                        ], style={"marginBottom": "20px"})
                    ], md=6),
            
            dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H4("Status do Sistema", className="text-white mb-0"),
                                style={"backgroundColor": "#20497e"}
                            ),
                            dbc.CardBody([
                                    status_layout,
                                    html.Div(debug_layout, style={
                                        "backgroundColor": "#f8f9fa",
                                        "padding": "10px",
                                        "border": "1px solid #ccc",
                                        "borderRadius": "5px",
                                        "fontFamily": "monospace",
                                        "fontSize": "0.9em",
                                        "color": "#000",
                                        "marginTop": "10px",
                                        "height": "52px",
                                        "overflowY": "auto"
                                    })
                            ], style={"backgroundColor": "#2a5a8f", "color": "white"})
                ], style={"marginBottom": "20px"})
            ], md=6)
        ]),
             
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H4("Histórico de Distância (últimas 24h)", className="text-white mb-0"),
                            style={"backgroundColor": "#20497e"}
                        ),
                        dbc.CardBody(
                            dcc.Graph(figure=fig_dist), 
                            style={"backgroundColor": "#2a5a8f", "color": "white"})
                    ], style={"marginBottom": "20px"})
                ], md=8),  
            
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            html.H4("Geolocalização do Sensor", className="text-white mb-0"),
                            style={"backgroundColor": "#20497e"}
                        ),
                        dbc.CardBody(
                            html.Iframe(srcDoc=open("mapa_sensor_0036.html", "r", encoding="utf-8").read(),
                                        width="100%", height="445 "), 
                            style={"backgroundColor": "#2a5a8f", "color": "white"})
                    ], style={"marginBottom": "20px"})
                ], md=4)
           ]),
            
           
        ], fluid=True) # Fim do Container
], style={"padding": "20px", "backgroundColor": "#173358"}), # Final do Layout do APP
    
    # Gráficos
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Histórico de Cota (Últimas 24h)", 
                        style={"backgroundColor": "#20497e", "color": "#fff"}),
            dbc.CardBody([
                dcc.Graph(id="grafico-cota-0036")
            ])
        ], style={"marginBottom": "20px"})
    ], ),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Histórico de Distância (Últimas 24h)", 
                              style={"backgroundColor": "#20497e", "color": "#fff"}),
                dbc.CardBody([
                    dcc.Graph(id="grafico-distancia-0036")
                ])
            ], style={"marginBottom": "20px"})
        ], ),
    ]),
    
    # Tabela com dados recentes
dbc.Row([
    dbc.Col([
        dbc.Card([
            dbc.CardHeader("Dados Recentes", 
                            style={"backgroundColor": "#20497e", "color": "#fff"}),
            dbc.CardBody([
                html.Div(id="tabela-dados-0036")
            ])
        ])
    ])
]),
    
# Componente de atualização automática
dcc.Interval(
    id='interval-0036',
    interval=20*1000,  # Atualiza a cada 30 segundos
    n_intervals=0
)
style={"backgroundColor": "#173358", "minHeight": "100vh", "padding": "20px"}

# Callback para atualizar os dados da página
@callback(
    [Output("distancia-atual-0036", "children"),
     Output("cota-atual-0036", "children"),
     Output("alerta-atual-0036", "children"),
     Output("temperatura-atual-0036", "children"),
     Output("grafico-cota-0036", "figure"),
     Output("grafico-distancia-0036", "figure"),
     Output("tabela-dados-0036", "children")],
    [Input("interval-0036", "n_intervals")]
)
def update_sensor_0036(n):
    try:
        # Busca dados atuais
        query_atual = "SELECT TOP 1 * FROM dados_sensores WHERE nome = '0036' ORDER BY data DESC"
        df_atual = pd.read_sql(query_atual, engine)
        
        # Busca dados históricos das últimas 24h
        query_hist = """
        SELECT * FROM dados_sensores 
        WHERE nome = '0036' AND data >= DATEADD(hour, -24, GETDATE())
        ORDER BY data ASC
        """
        df_hist = pd.read_sql(query_hist, engine)
        
        if df_atual.empty:
            return "--", "--", "--", "--", {}, {}, "Sem dados disponíveis"
        
        # Valores atuais
        distancia = f"{df_atual['distancia'].iloc[0]:.2f} cm" if 'distancia' in df_atual.columns else "--"
        cota = f"{df_atual['cota'].iloc[0]:.2f}" if 'cota' in df_atual.columns else "--"
        alerta = f"{df_atual['percentual_alerta'].iloc[0]:.2f}%" if 'percentual_alerta' in df_atual.columns else "--"
        temperatura = f"{df_atual['temperatura'].iloc[0]:.1f}°C" if 'temperatura' in df_atual.columns else "--"
        
        # Gráfico de Cota
        fig_cota = go.Figure()
        if not df_hist.empty and 'cota' in df_hist.columns:
            fig_cota.add_trace(go.Scatter(
                x=df_hist['data'],
                y=df_hist['cota'],
                mode='lines+markers',
                name='Cota',
                line=dict(color='#1E90FF', width=2)
            ))
        
        fig_cota.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            title="Variação da Cota"
        )
        
        # Gráfico de Distância
        fig_dist = go.Figure()
        if not df_hist.empty and 'distancia' in df_hist.columns:
            fig_dist.add_trace(go.Scatter(
                x=df_hist['data'],
                y=df_hist['distancia'],
                mode='lines+markers',
                name='Distância',
                line=dict(color='#FFA500', width=2)
            ))
        
        fig_dist.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.2)'),
            title="Variação da Distância"
        )
        
        # Tabela com últimos dados
        query_recentes = "SELECT TOP 10 * FROM dados_sensores WHERE nome = '0036' ORDER BY data DESC"
        df_recentes = pd.read_sql(query_recentes, engine)
        
        if not df_recentes.empty:
            tabela = dbc.Table.from_dataframe(
                df_recentes[['data', 'distancia', 'cota', 'percentual_alerta', 'temperatura']].round(2),
                striped=True, 
                bordered=True, 
                hover=True,
                style={'color': 'white'}
            )
        else:
            tabela = html.P("Sem dados recentes disponíveis", style={'color': 'white'})
        
        return distancia, cota, alerta, temperatura, fig_cota, fig_dist, tabela
        
    except Exception as e:
        print(f"Erro ao atualizar sensor 0036: {str(e)}")
        return "Erro", "Erro", "Erro", "Erro", {}, {}, f"Erro: {str(e)}"