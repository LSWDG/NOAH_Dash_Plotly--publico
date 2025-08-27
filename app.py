# -*- coding: utf-8 -*-
# Importações necessárias para o Dash, roteamento e manipulação de dados.
import dash
from dash import Dash, html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine
import urllib

# ========== CONFIGURAÇÃO DE CORES DINÂMICAS ==========
# Este dicionário contém os limites para determinar as cores dos indicadores
# com base na cota e no percentual de alerta.
PARAMETROS = {
    # Parâmetros para COTA
    "COTA": {
        "0032": {"observacao": (0, 5.40),"alerta": (5.41, 7.38),"critico": (7.39, float('inf'))},
        "0033": {"observacao": (0, 10.85),"alerta": (10.86, 12.46),"critico": (12.47, float('inf'))},
        "0034": {"observacao": (0, 1.71),"alerta": (1.72, 2.69),"critico": (2.70, float('inf'))},
        "0035": {"observacao": (0, 7.80),"alerta": (7.81, 9.50),"critico": (9.51, float('inf'))},
        "0037": {"observacao": (0, 1.24),"alerta": (1.25, 2.24),"critico": (2.25, float('inf'))},
        "0038": {"observacao": (0, 4.44),"alerta": (4.45, 5.52),"critico": (5.53, float('inf'))},
        "0039": {"observacao": (0, 62.39),"alerta": (62.40, 65.12),"critico": (65.13, float('inf'))},
        "0046": {"observacao": (0, 7.85),"alerta": (7.86, 10.02),"critico": (10.03, float('inf'))},
        "0049": {"observacao": (0, 0.51),"alerta": (0.52, 1.94),"critico": (1.95, float('inf'))},
        "0053": {"observacao": (0, 12.31),"alerta": (12.32, 13.10),"critico": (13.11, float('inf'))},
        "0056": {"observacao": (0, 10.40),"alerta": (10.41, 11.65),"critico": (11.66, float('inf'))},
        "0058": {"observacao": (0, 23.00),"alerta": (23.01, 23.85),"critico": (23.86, float('inf'))},
        "0060": {"observacao": (0, 12.73),"alerta": (12.74, 14.33),"critico": (14.34, float('inf'))},
        "AJ-40": {"observacao": (0, 2.82),"alerta": (2.83, 4.34),"critico": (4.35, float('inf'))}
    },
    # Parâmetros para %ALERTA (com faixas diferentes)
    "ALERTA": {
        "0032": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0033": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0034": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0035": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0037": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0038": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0039": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0046": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0049": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0053": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0056": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0058": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "0060": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))},
        "AJ-40": {"observacao": (0, 38), "atencao": (39, 73), "alerta": (74, 99), "critico": (100, float('inf'))}
    }
}

def get_cor(valor, sensor_id, tipo="COTA"):
    """Retorna cor pela faixa correta, usando [min, max]."""
    try:
        if valor is None or (isinstance(valor, float) and pd.isna(valor)):
            return "#FFFFFF"

        # aceita número, "5,88", "5.88", "5.88%"
        v = str(valor).strip().replace("%", "").replace(",", ".")
        v = float(v)

        params_tipo = PARAMETROS.get(tipo, {})
        params = params_tipo.get(str(sensor_id))
        if not params:
            print(f"[get_cor] Parâmetros não encontrados para {sensor_id} ({tipo})")
            return "#FFFFFF"

        def in_range(x, faixa):
            a, b = faixa
            if b == float("inf"):
                return x >= a
            return a <= x <= b

        if tipo == "COTA":
            if in_range(v, params["observacao"]): return "#1E90FF"  # azul
            if in_range(v, params["alerta"]):     return "#FFA500"  # laranja
            if in_range(v, params["critico"]):    return "#FF4500"  # vermelho
            return "#FFFFFF"

        elif tipo == "ALERTA":
            if in_range(v, params["observacao"]): return "#1E90FF"  # azul
            if in_range(v, params["atencao"]):    return "#FFD700"  # amarelo
            if in_range(v, params["alerta"]):     return "#FFA500"  # laranja
            if in_range(v, params["critico"]):    return "#FF4500"  # vermelho
            return "#FFFFFF"

        else:
            return "#FFFFFF"

    except Exception as e:
        print(f"[get_cor] Erro para {sensor_id} ({tipo}): {e}")
        return "#FFFFFF"


# === CONFIGURAÇÃO DA CONEXÃO COM O BANCO DE DADOS ===
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=10.5.232.43;"             
    "DATABASE=NivelRios;"             
    "UID=user_nivel_rio;"             
    "PWD=nra2bLcpRbb03O1"             
)
# engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
engine = create_engine(f"mssql+pymssql://{user_nivel_rio}:{nra2bLcpRbb03O1}@{10.5.232.43}:{1433}/{NivelRios}")


# === DEFINIÇÃO DE QUERIES SQL ===
query_ultimos = """
WITH ultimos AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY nome ORDER BY data DESC) AS rn
    FROM dados_sensores
)
SELECT * FROM ultimos WHERE rn = 1
"""

# === LISTA DE SENSORES ===
# Defina os IDs e nomes dos sensores. Isso permite que o código seja
# escalável e os layouts sejam gerados dinamicamente.
sensores = [
    {"nome": "0030", "endereco": "BANGU - Rua da Feira"},
    {"nome": "0031", "endereco": "Viaduto dos Marinheiros"},
    {"nome": "0032", "endereco": "Rio Trapicheiro - Largo São Maron"},
    {"nome": "0033", "endereco": "Pç. Luis La Saigne x Av. Maracanã"},
    {"nome": "0034", "endereco": "ETE Pavuna"},
    {"nome": "0035", "endereco": "Rio Joana - São Francisco Xavier"},
    {"nome": "0036", "endereco": "Rio Joana x Barão de São Francisco"},
    {"nome": "0037", "endereco": "Dutra"},
    {"nome": "0038", "endereco": "KIOTO - Paulo de Frontin"},
    {"nome": "0039", "endereco": "Furnas"},
    {"nome": "0046", "endereco": "Mont Reservatório Prç Niterói"},
    {"nome": "0049", "endereco": "Ponte do Dique"},
    # {"nome": "0050", "endereco": "Rua Maxwell x Barão de São Franciscot"},
    {"nome": "0052", "endereco": "Francisco Eugênio - 4º Batalhão PM"},
    {"nome": "0053", "endereco": "Rio Trapicheiros x Conde Bonfim"},
    {"nome": "0056", "endereco": "Praça Varnhagen"},
    # {"nome": "0057", "endereco": "FURTO - Praça Varnhagen"},
    {"nome": "0058", "endereco": "Rua Uruguai x AV. Maracanã"},
    {"nome": "0060", "endereco": "Rio Joana x Boulevard"},
    {"nome": "0061", "endereco": "COMLURB - Paulo de Frontin"},
    # {"nome": "0066", "endereco": "Francisco Eugênio - 4º Batalhão PM"},
    {"nome": "0067", "endereco": "Lagoa Rodrigo de Freitas"},
    # {"nome": "AJ-31", "endereco": "Rio Joana - São Francisco Xavier"},
    {"nome": "AJ-40", "endereco": "Fazenda Botafogo"}
]

# === FUNÇÕES DE LAYOUT ===
def cria_card_sensor(nome, endereco):
    """
    Função que cria o layout de um único cartão de sensor.
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                f"Sensor {nome}",
                style={
                    "height": "50px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "padding": "10px",
                    "fontWeight": "bold",
                    "fontSize": "23px",
                    "backgroundColor": "#20497e",
                    "color": "#fff",
                    "text-shadow": "1px 1px 1px #000000"
                },
                className="rounded-top"
            ),
            dbc.CardBody(
                [
                    # Componente de distância
                    html.Div(
                        "--",
                        id=f"{nome}-distancia",
                        style={
                            "height": "40px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "color": "#f8f9fa",
                            "margin": "5px 0",
                            "text-shadow": "1px 1px 1px #000000"
                        }
                    ),
                    
                    # Linha de rótulos
                    html.Div(
                        [
                            html.Span("Cota", style={
                                "display": "inline-block",
                                "width": "50%",
                                "textAlign": "center",
                                "color": "#FFFFFF",
                                "fontSize": "12px",
                                "fontWeight": "bold",
                                "paddingRight": "20px"
                            }),
                            html.Span("% Alerta", style={
                                "display": "inline-block",
                                "width": "50%",
                                "textAlign": "center",
                                "color": "#FFFFFF",
                                "fontSize": "12px",
                                "fontWeight": "bold",
                                "paddingLeft": "20px"
                            })
                        ],
                        style={
                            "textAlign": "center",
                            "margin": "0 auto",
                            "width": "90%"
                        }
                    ),
                    
                    # Linha de valores de COTA e ALERTA
                    html.Div(
                        [
                            html.Span(
                                "--",
                                id=f"{nome}-cota",
                                style={
                                    "display": "inline-block",
                                    "width": "50%",
                                    "textAlign": "center",
                                    "fontSize": "16px",
                                    "fontWeight": "bold",
                                    "paddingRight": "20px"
                                }
                            ),
                            html.Span(
                                "--",
                                id=f"{nome}-alerta",
                                style={
                                    "display": "inline-block",
                                    "width": "50%",
                                    "textAlign": "center",
                                    "fontSize": "16px",
                                    "fontWeight": "bold",
                                    "paddingLeft": "20px"
                                }
                            )
                        ],
                        style={
                            "textAlign": "center",
                            "margin": "0 auto 10px",
                            "width": "90%"
                        }
                    ),
                    
                    html.Div(
                        endereco,
                        style={
                            "height": "40px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "fontSize": "14px",
                            "color": "#f8f9fa",
                            "textAlign": "center",
                            "overflow": "hidden",
                            "textOverflow": "ellipsis",
                            "padding": "0 5px"
                        }
                    )
                ],
                style={
                    "padding": "10px",
                    "backgroundColor": "#2a5a8f",
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "space-between"
                },
                className="rounded-bottom"
            ),
            # Botão "Acessar Sensor"
            dbc.CardFooter(
                dbc.Button(
                    [html.I(className="fas fa-chart-line me-2"), "Acessar Sensor"],
                    href=f"/{nome}",  # Link para a página do sensor
                    color="link",
                    className="w-100",
                    style={"text-decoration": "none", "color": "#f8f9fa", "font-weight": "bold", "padding": "0.5px"}
                ),
                style={"backgroundColor": "#20497e", "borderTop": "1px solid #2a5a8f"}
            )
        ],
        style={
            "width": "250px",
            "height": "260px",
            "margin": "10px",
            "borderRadius": "15px",
            "overflow": "hidden",
            "boxShadow": "0 4px 8px rgba(0,0,0,0.25)"
        }
    )

def create_dashboard_layout():
    """
    Função que cria o layout do dashboard principal com os cards dos sensores.
    """
    return html.Div([
        # Indicador de última atualização
        html.Div(
            id="ultima-atualizacao",
            style={
                "color": "#f8f9fa", 
                "textAlign": "right", 
                "marginTop": "10px", 
                "fontWeight": "bold", 
                "fontSize": "16px",
                "paddingRight": "20px"
            }
        ),
        
        # Container dos cards
        html.Div(
            id="cards-container",
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(auto-fill, minmax(250px, 1fr))",
                "gap": "15px",
                "padding": "20px",
                "justifyItems": "center"
            },
            children=[cria_card_sensor(s["nome"], s["endereco"]) for s in sensores]
        )
    ])

# Função para importar páginas dinamicamente
def import_sensor_page(sensor_name):
    """
    Importa o layout de uma página de sensor específica.
    """
    try:
        # Importa o módulo da página do sensor
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            f"page_{sensor_name}", 
            f"pages/{sensor_name}.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Retorna o layout da página
        if hasattr(module, 'layout'):
            return module.layout
        else:
            return html.Div([
                html.H2(f"Sensor {sensor_name}", style={"color": "#f8f9fa", "textAlign": "center"}),
                html.P("Layout não encontrado na página.", style={"color": "#f8f9fa", "textAlign": "center"})
            ])
    except Exception as e:
        return html.Div([
            html.H2(f"Erro ao carregar a página do Sensor {sensor_name}", style={"color": "#dc3545", "textAlign": "center"}),
            html.P(f"Erro: {str(e)}", style={"color": "#f8f9fa", "textAlign": "center"}),
            html.P(f"Verifique se o arquivo pages/{sensor_name}.py existe.", 
                   style={"color": "#f8f9fa", "textAlign": "center"})
        ])

# === INICIALIZAÇÃO DO APP DASH ===
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;700&display=swap",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
])
app.title = "Dados dos Sensores do NOAH"

# Usado para fazer o DEPLOY no render.com
server = app.server

# === LAYOUT PRINCIPAL ===
app.layout = html.Div([
    dcc.Interval(id='interval-atualizacao', interval=20*1000, n_intervals=0),
    dcc.Location(id='url', refresh=False),
    
    
    # Menu Lateral (Offcanvas)
    dbc.Offcanvas(
        [
            html.Div(
                [
                    # Você precisará ter a imagem 'Logo branco sem fundo.png' na pasta 'assets'
                    html.Img(src="/assets/Logo branco sem fundo.png", 
                           style={"width": "100%", "padding": "10px"}),
                    html.Hr()
                ],
                className="text-center"
            ),
            dbc.Nav(
                [
                    dbc.NavLink(
                        [html.I(className="fas fa-home me-2"), "Dashboard"],
                        href="/",
                        active="exact",
                        className="nav-link-custom"
                    ),
                    # dbc.NavLink(
                    #     dbc.Button(
                    #         [html.I(className="fas fa-solid fa-water me-2"), "Todos os Sensores"],
                    #         id="btn-sensores",
                    #         color="link",
                    #         className="nav-link-custom",
                    #         style={"textDecoration": "none", "width": "100%", "textAlign": "left"}
                    #     ),
                    #     href="#",
                    #     className="p-0 m-0"
                    # ),
                    # dbc.Collapse(
                    #     dbc.Nav(
                    #         [
                    #             # Loop para gerar links para cada sensor
                    #             dbc.NavLink(f"Sensor {s['nome']}", href=f"/{s['nome']}", className="ps-4 submenu-link")
                    #             for s in sensores
                    #         ],
                    #         vertical=True,
                    #     ),
                    #     id="collapse-sensores",
                    #     is_open=False
                    # ),
                    dbc.NavLink(
                        [html.I(className="fas fa-chart-line me-2"), "Gráficos"],
                        href="/graficos",
                        active="exact",
                        className="nav-link-custom"
                    ),
                    dbc.NavLink(
                        [html.I(className="fas fa-cog me-2"), "Configurações"],
                        href="/config",
                        active="exact",
                        className="nav-link-custom"
                    ),
                ],
                vertical=True,
                pills=True,
                className="mb-3"
            ),
            html.Hr(),
            html.P("Banco de dados dos", 
                  className="text-center",
                  style={"color": "#aaa", "marginBottom": "0"}),
            html.P("Sensores NOAH - Rio Águas", 
                  className="text-center",
                  style={"color": "#aaa", "marginBottom": "0"}),
            html.Br(),
            html.P("Desenvolvido por",
                   className="text-center",
                  style={"color": "#aaa", "marginBottom": "0"}),
            html.P("Leandro Di Giorgio",
                   className="text-center",
                  style={"color": "#aaa", "marginBottom": "0"})          
        ],
        id="offcanvas",
        is_open=False,
        placement="start",
        backdrop=True,
        style={"width": "280px", "backgroundColor": "#173358"}
    ),
    
    # Conteúdo principal
    html.Div([
        # Cabeçalho com botão do menu
        dbc.Row(
            dbc.Col(
                [
                    # Linha superior (botão, logo e título)
                    html.Div(
                        [
                            # Botão do menu
                            dbc.Button(
                                html.I(className="fas fa-bars-staggered"),
                                id="open-offcanvas",
                                n_clicks=0,
                                style={
                                    "margin": "0",
                                    "padding": "0 10px",
                                    "background": "transparent",
                                    "border": "none",
                                    "boxShadow": "none",
                                    "color": "#f8f9fa",
                                    "fontSize": "24px",
                                    "marginRight": "15px"
                                },
                                className="p-0"
                            ),
                            
                            # Título H1
                            html.H1("Dados dos Sensores do NOAH", 
                                    className="H1",
                                    style={"margin": "0", "color": "#f8f9fa", "fontWeight": "700"}
                            ),
                            
                            # Imagem do logo
                            html.Img(
                                # Você precisará ter a imagem 'favicon.ico' na pasta 'assets'
                                src="/assets/favicon.ico",
                                style={
                                    "height": "50px",
                                    "marginRight": "15px",
                                    "marginLeft": "15px"
                                }
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "center",
                            "flexWrap": "nowrap"
                        }
                    ),
                    
                    # Descrição (P) abaixo
                    html.P(
                        "Dados provenientes do banco de dados da Rio Águas com Latitude, Longitude, Temperatura, Umidade, Chuva, Cota e Percentual de Alerta",
                        className="P",
                        style={"marginTop": "10px", "color": "#ccc"}
                    )
                ],
            style={"width": "100%"}
        ),className="div-cabecalho"
        ),
        
        # CONTAINER PARA O CONTEÚDO DAS PÁGINAS
        html.Div(
            id="page-content",
            children=create_dashboard_layout()  # Página inicial
        )
        
    ], 
    style={"backgroundColor": "#173358", "minHeight": "100vh"} # Cor do fundo da página dos cards
    )
], 
className="app-container",
style={"minHeight": "100vh", "backgroundColor": "#1a1a2e", "fontFamily": "Poppins"}
)

# ========== CALLBACKS ==========

# Callback para abrir/fechar o menu lateral
@app.callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    State("offcanvas", "is_open"),
)
def toggle_offcanvas(n, is_open):
    if n:
        return not is_open
    return is_open

# Callback para abrir/fechar a lista de sensores
# @app.callback(
#     Output("collapse-sensores", "is_open"),
#     Input("btn-sensores", "n_clicks"),
#     State("collapse-sensores", "is_open")
# )
# def toggle_sensores(n, is_open):
#     if n:
#         return not is_open
#     return is_open

# CALLBACK PRINCIPAL PARA NAVEGAÇÃO
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/' or pathname is None:
        # Página inicial - Dashboard com cards
        return create_dashboard_layout()
    
    elif pathname == '/graficos':
        return html.Div([
            html.H2("Gráficos", style={"color": "#f8f9fa", "textAlign": "center"}),
            html.P("Página de gráficos em desenvolvimento.", style={"color": "#f8f9fa", "textAlign": "center"})
        ], className="container py-5")
    
    elif pathname == '/config':
        return html.Div([
            html.H2("Configurações", style={"color": "#f8f9fa", "textAlign": "center"}),
            html.P("Página de configurações em desenvolvimento.", style={"color": "#f8f9fa", "textAlign": "center"})
        ], className="container py-5")
    
    else:
        # Verifica se é uma página de sensor
        sensor_name = pathname[1:]  # Remove a barra inicial
        sensor_names = [s["nome"] for s in sensores]
        
        if sensor_name in sensor_names:
            # Carrega a página específica do sensor
            return import_sensor_page(sensor_name)
        else:
            # Página não encontrada
            return html.Div([
                html.H2("404 - Página não encontrada", style={"color": "#dc3545", "textAlign": "center"}),
                html.P(f"A rota '{pathname}' não existe.", style={"color": "#f8f9fa", "textAlign": "center"}),
                dbc.Button("Voltar ao Dashboard", href="/", color="secondary", className="mt-3")
            ], className="container py-5 text-center")

# CALLBACK PARA ATUALIZAR OS VALORES DOS CARDS (APENAS QUANDO ESTIVER NO DASHBOARD)
@app.callback(
    [
        Output(f"{s['nome']}-distancia", "children") for s in sensores
    ] + [
        Output(f"{s['nome']}-cota", "children") for s in sensores
    ] + [
        Output(f"{s['nome']}-alerta", "children") for s in sensores
    ] + [
        Output(f"{s['nome']}-cota", "style") for s in sensores
    ] + [
        Output(f"{s['nome']}-alerta", "style") for s in sensores
    ] + [
        Output("ultima-atualizacao", "children")
    ],
    Input("interval-atualizacao", "n_intervals"),
    prevent_initial_call=True
)
def atualizar_valores(n):
    """
    Função que atualiza os dados nos cards do dashboard.
    """
    try:
        df_atualizado = pd.read_sql(query_ultimos, engine)
        
        distancias = []
        cotas = []
        alertas = []
        estilos_cota = []
        estilos_alerta = []
        
        for sensor in sensores:
            sensor_data = df_atualizado[df_atualizado['nome'] == sensor['nome']]
            
            # Função auxiliar melhorada para conversão segura
            def formatar_valor(valor, sufixo=''):
                try:
                    if pd.isna(valor) or valor in [None, '']:
                        return "--"
                    valor_str = str(valor).replace(',', '.').strip()
                    if not valor_str.replace('.', '').isdigit():
                        return "--"
                    return f"{float(valor_str):.2f}{sufixo}"
                except:
                    return "--"
            
            # 1. Distância (children)
            distancia = sensor_data['distancia'].iloc[0] if not sensor_data.empty and 'distancia' in sensor_data.columns else None
            distancias.append(formatar_valor(distancia, ' cm'))
            
            # 2. Cota (children)
            cota = sensor_data['cota'].iloc[0] if not sensor_data.empty and 'cota' in sensor_data.columns else None
            cotas.append(formatar_valor(cota))
            
            # 3. Alerta (children)
            alerta = sensor_data['percentual_alerta'].iloc[0] if not sensor_data.empty and 'percentual_alerta' in sensor_data.columns else None
            alertas.append(formatar_valor(alerta, '%'))
            
            # 4. Estilo Cota - mantendo layout e adicionando cor dinâmica
            try:
                cota_float = float(str(cota).replace(',', '.')) if cota not in [None, ''] else None
                cor_cota = get_cor(cota_float, sensor['nome'])
                estilos_cota.append({
                    "color": cor_cota,
                    "display": "inline-block",
                    "width": "50%",
                    "textAlign": "center",
                    "fontSize": "16px",
                    "fontWeight": "bold",
                    "paddingRight": "20px"
                })
            except:
                estilos_cota.append({
                    "color": "#FFFFFF",
                    "display": "inline-block",
                    "width": "50%",
                    "textAlign": "center",
                    "fontSize": "16px",
                    "fontWeight": "bold",
                    "paddingRight": "20px"
                })
            
            # 5. Estilo Alerta - mantendo layout e adicionando cor dinâmica
            try:
                alerta_float = float(str(alerta).replace(',', '.')) if alerta not in [None, ''] else None
                cor_alerta = get_cor(alerta_float, sensor['nome'], tipo="ALERTA")
                estilos_alerta.append({
                    "color": cor_alerta,
                    "display": "inline-block",
                    "width": "50%",
                    "textAlign": "center",
                    "fontSize": "16px",
                    "fontWeight": "bold",
                    "paddingLeft": "20px"
                })
            except:
                estilos_alerta.append({
                    "color": "#FFFFFF",
                    "display": "inline-block",
                    "width": "50%",
                    "textAlign": "center",
                    "fontSize": "16px",
                    "fontWeight": "bold",
                    "paddingLeft": "20px"
                })
        
        return distancias + cotas + alertas + estilos_cota + estilos_alerta + [
            f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        ]
    
    except Exception as e:
        print(f"Erro na atualização: {str(e)}")
        num_sensores = len(sensores)
        return (
            ["--"] * num_sensores +  # distancias
            ["--"] * num_sensores +  # cotas
            ["--"] * num_sensores +  # alertas
            [{
                "color": "#FFFFFF",
                "display": "inline-block",
                "width": "50%",
                "textAlign": "center",
                "fontSize": "16px",
                "fontWeight": "bold",
                "paddingRight": "20px"
            }] * num_sensores +  # estilos_cota
            [{
                "color": "#FFFFFF",
                "display": "inline-block",
                "width": "50%",
                "textAlign": "center",
                "fontSize": "16px",
                "fontWeight": "bold",
                "paddingLeft": "20px"
            }] * num_sensores +  # estilos_alerta
            ["Erro na atualização"]
        )


if __name__ == "__main__":
    app.run(debug=True)



