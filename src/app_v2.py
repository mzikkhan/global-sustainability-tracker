import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os




    
# --- data wrangling ---
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'WorldSustainabilityDataset.csv')
df = pd.read_csv(DATA_PATH)

col_mapping = {
    'Country Name': 'Country',
    'Access to electricity (% of population) - EG.ELC.ACCS.ZS': 'Elec_Access',
    'GDP (current US$) - NY.GDP.MKTP.CD': 'GDP',
    'Annual production-based emissions of carbon dioxide (CO2), measured in million tonnes': 'CO2_Emissions',
    'Life expectancy at birth, total (years) - SP.DYN.LE00.IN': 'Life_Exp',
    'Proportion of seats held by women in national parliaments (%) - SG.GEN.PARL.ZS': 'Women_Parliament',
    'Adjusted savings: carbon dioxide damage (% of GNI) - NY.ADJ.DCO2.GN.ZS': 'CO2_Damage_GNI',
    'Adjusted savings: natural resources depletion (% of GNI) - NY.ADJ.DRES.GN.ZS': 'Nat_Res_Depletion',
    'Inflation, consumer prices (annual %) - FP.CPI.TOTL.ZG': 'Inflation',
    'Regime Type (RoW Measure Definition)': 'Regime_Type',
    'World Regions (UN SDG Definition)': 'SDG_Region',
    'Income Classification (World Bank Definition)': 'Income_Group'
}
df.rename(columns=col_mapping, inplace=True)


df_filtered = df.dropna(subset=['Continent', 'Year']).copy()
df_filtered['Year'] = pd.to_datetime(df_filtered['Year'], format='%Y')
df_filtered['Year_num'] = df_filtered['Year'].dt.year

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}<title>Sustainability Hub</title>{%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            body { background-color: #f0f4f8; font-family: 'Inter', sans-serif; color: #334155; }
            .nav-link { font-weight: 700; color: #64748b; margin-left: 20px; text-decoration: none; font-size: 0.9rem; }
            .nav-link:hover { color: #298c8c; }
            .kpi-card { 
                background-color: #ffffff; border-radius: 8px; padding: 20px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; 
                border-top: 5px solid #298c8c !important; 
            }
            .kpi-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px rgba(0,0,0,0.1);
                }
            .chart-card { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            .kpi-title { font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px; }
            .kpi-value { font-size: 1.8rem; font-weight: 800; color: #0f172a; margin-bottom: 5px; }
            .kpi-sub { font-size: 0.8rem; color: #64748b; font-weight: 600; }
            .text-success { color: #10b981 !important; }
            .text-danger { color: #ef4444 !important; }
            .dashboard-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 0; border-bottom: 3px solid #298c8c; margin-bottom: 30px; }
            .dashboard-title { font-weight: 800; color: #0f172a; font-size: 1.8rem; margin: 0; }
        </style>
    </head>
    <body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body>
</html>
'''

def create_kpi_card(id_prefix, title, tooltip=""):
    return html.Div(className='kpi-card', children=[
        html.Div([
            html.Span(title, className='kpi-title'),
            html.Span(" ⓘ", id=f"{id_prefix}-info", style={"cursor":"pointer","marginLeft":"5px"})
        ]),
        
        dbc.Tooltip(
            tooltip,
            target=f"{id_prefix}-info",
            placement="top"
        ),

        html.Div(id=f'{id_prefix}-v', className='kpi-value', children='-'),
        html.Div(id=f'{id_prefix}-s', className='kpi-sub', children='-'),

        
    ])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Container([
        html.Div(className='dashboard-header', children=[
            html.H1("GLOBAL SUSTAINABILITY TRACKER", className='dashboard-title'),
            html.Div([
                dcc.Link("Main Dashboard", href="/", className="nav-link"),
                dcc.Link("Multi-Country Compare", href="/compare", className="nav-link"),
            ])
        ]),
        html.Div(id='page-content')
    ], fluid=True, className="px-4")
])

def layout_main():
    return html.Div([
        dbc.Row([
            dbc.Col(md=6, children=[
                html.Div(
                className='chart-card p-3 mb-4',style={'border':'1px solid #e2e8f0','minHeight':'140px'},
                    children=[
                    dbc.Row([
                        dbc.Col(md=4, children=[html.Div("GROUP", className='kpi-title'), dcc.Dropdown(id='group-dropdown', options=[{'label': k.replace('_',' '), 'value': k} for k in ['Continent','Country','Income_Group','SDG_Region']], value='Continent', clearable=False)]),
                        dbc.Col(md=4, children=[html.Div("SELECTION", className='kpi-title'), dcc.Dropdown(id='entity-dropdown', clearable=False)]),
                        dbc.Col(md=4, children=[html.Div("YEAR RANGE", className='kpi-title'), dcc.RangeSlider(id='year-slider', min=2000, max=2020, value=[2000, 2018], step=1, marks=None, tooltip={"always_visible": True, "placement": "bottom"})])
                    ])
                ])
            ]),
        dbc.Col(md=6, children=[
            dbc.Row(
                align="stretch",
                children=[
                    dbc.Col(create_kpi_card(
    'kpi-co2',
    'CO2 EMISSIONS (M Tonnes)',
    tooltip="Measures carbon dioxide emissions generated annually. Higher values indicate greater environmental impact."
), className="h-100"),
                    dbc.Col(create_kpi_card(
    'kpi-gdp',
    'GDP (USD)',
    tooltip="Gross Domestic Product represents the total monetary value of goods and services produced in the region."
), className="h-100"),
                    dbc.Col(create_kpi_card(
    'kpi-nat',
    'NAT RES DEPLETION (%)',
    tooltip="Percentage of natural resource value extracted relative to national income. Higher values suggest unsustainable resource use."
), className="h-100")
                ]
            )
        ])
        ]),
        dbc.Row([
            dbc.Col(md=6, children=[
                html.Div(className='chart-card', children=[
                    dbc.Row(align="center", children=[
                        dbc.Col(html.Div([html.Span(id='bubble-title', className='fw-bold', style={'fontSize':'1.1rem'}), dbc.Button("Reset", id="reset-btn", color="outline-secondary", size="sm", className="ms-2")]), width=6),
                        dbc.Col(dcc.Dropdown(id='bubble-y-drop', options=[{'label': 'CO2 Emissions', 'value': 'CO2_Emissions'}, {'label': 'CO2 Damage', 'value': 'CO2_Damage_GNI'}, {'label': 'Electricity Access', 'value': 'Elec_Access'}], value='CO2_Emissions', clearable=False), width=6)
                    ]),
                    dcc.Graph(id='bubble-chart', style={'height': '500px', 'marginTop': '20px'})
                ])
            ]),
            dbc.Col(md=4, children=[
                html.Div(className='chart-card mb-3', children=[
                    dbc.Row([dbc.Col(html.Div(id='econ-title', className='fw-bold'), width=7), dbc.Col(dcc.Dropdown(id='econ-drop', options=[{'label':'GDP','value':'GDP'},{'label':'Inflation','value':'Inflation'}], value='GDP', clearable=False), width=5)]),
                    dcc.Graph(id='econ-chart', style={'height': '220px'})
                ]),
                html.Div(className='chart-card', children=[
                    dbc.Row([dbc.Col(html.Div(id='sdg-title', className='fw-bold'), width=7), dbc.Col(dcc.Dropdown(id='sdg-drop', options=[{'label':'Life Expectancy','value':'Life_Exp'},{'label':'Women Representation','value':'Women_Parliament'}], value='Life_Exp', clearable=False), width=5)]),
                    dcc.Graph(id='sdg-chart', style={'height': '220px'})
                ])
            ]),
            dbc.Col(md=2, children=[
                create_kpi_card(
                        'kpi-inf',
                        'INFLATION (%)',
                        tooltip="Inflation measures the annual percentage increase in the general price level of goods and services. Moderate inflation is normal in growing economies, but high inflation can reduce purchasing power and economic stability."
                    ),
                html.Div(className='kpi-card', children=[html.Div("REGIME TYPE", className='kpi-title'), html.Div(id='kpi-reg-v', className='fw-bold', style={'fontSize': '1rem', 'marginTop':'5px'})]),
                create_kpi_card(
                    'kpi-hlt',
                    'HEALTH (LIFE EXP)',
                    tooltip="Life expectancy indicates the average number of years a newborn is expected to live if current mortality patterns continue. It is a key indicator of overall population health, healthcare access, and living conditions."
                )
            ])
        ])
    ])

def layout_compare():
    return html.Div([
        dbc.Row([dbc.Col(md=12, children=[html.Div(className='chart-card mb-4', children=[html.Div("COMPARE MULTIPLE COUNTRIES", className='kpi-title'), dcc.Dropdown(id='compare-dropdown', options=[{'label': c, 'value': c} for c in sorted(df_filtered['Country'].unique())], value=['Canada', 'China'], multi=True)])])]),
        dbc.Row([
            dbc.Col(md=6, children=[html.Div(className='chart-card', children=[html.Div("GDP GROWTH", className='fw-bold'), dcc.Graph(id='compare-gdp-chart')])]),
            dbc.Col(md=6, children=[html.Div(className='chart-card', children=[html.Div("CO2 EMISSIONS", className='fw-bold'), dcc.Graph(id='compare-co2-chart')])])
        ])
    ])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(p):
    return layout_compare() if p == '/compare' else layout_main()

@app.callback([Output('compare-gdp-chart','figure'), Output('compare-co2-chart','figure')], [Input('compare-dropdown','value')])
def update_comp(s):
    if not s: return {}, {}
    f = df_filtered[df_filtered['Country'].isin(s)]
    return px.line(f, x='Year', y='GDP', color='Country', markers=True, template='plotly_white'), \
           px.line(f, x='Year', y='CO2_Emissions', color='Country', markers=True, template='plotly_white')

@app.callback(
    [Output("bubble-y-drop", "options"),
     Output("bubble-y-drop", "value")],
    Input("group-dropdown", "value")
)
def update_bubble_dropdown(group):
    if group == "Country":
        options = [
            {"label": "GDP", "value": "GDP"},
            {"label": "Life Expectancy", "value": "Life_Exp"},
            {"label": "Electricity Access", "value": "Elec_Access"},
            {"label": "CO2 Damage", "value": "CO2_Damage_GNI"},
            {"label": "Inflation", "value": "Inflation"},
            {"label": "Natural Resource Depletion", "value": "Nat_Res_Depletion"},
        ]
        default_value = "GDP"
    else:
        options = [
            {"label": "CO2 Emissions", "value": "CO2_Emissions"},
            {"label": "CO2 Damage", "value": "CO2_Damage_GNI"},
            {"label": "Electricity Access", "value": "Elec_Access"},
        ]
        default_value = "CO2_Emissions"
    return options, default_value

@app.callback(
    [Output('bubble-chart', 'figure'), Output('econ-chart', 'figure'), Output('sdg-chart', 'figure'),
     Output('bubble-title', 'children'), Output('econ-title', 'children'), Output('sdg-title', 'children'),
     Output('kpi-co2-v','children'), Output('kpi-co2-s','children'),
     Output('kpi-gdp-v','children'), Output('kpi-gdp-s','children'),
     Output('kpi-nat-v','children'), Output('kpi-nat-s','children'),
     Output('kpi-inf-v','children'), Output('kpi-inf-s','children'),
     Output('kpi-hlt-v','children'), Output('kpi-hlt-s','children'),
     Output('kpi-reg-v','children'), Output('bubble-chart', 'clickData'),
     Output('entity-dropdown', 'options'), Output('entity-dropdown', 'value')],
    [Input('group-dropdown','value'), Input('entity-dropdown','value'), Input('year-slider','value'),
     Input('bubble-y-drop','value'), Input('econ-drop','value'), Input('sdg-drop','value'),
     Input('bubble-chart', 'clickData'), Input('reset-btn', 'n_clicks'), Input('url', 'pathname')]
)
def update_main(g, e, y, by, ed, sd, clickData, n_clicks, path):
    if path != '/': return [dash.no_update]*20
    ctx = dash.callback_context
    trig = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    opts = sorted(df_filtered[g].dropna().unique())
    e_opts = [{'label': i, 'value': i} for i in opts]
    e_val = e if e in opts else opts[0]
    
    if trig == 'reset-btn': clickData = None
    
    r_df = df_filtered[(df_filtered[g]==e_val) & (df_filtered['Year'].dt.year>=y[0]) & (df_filtered['Year'].dt.year<=y[1])]
    
    if r_df.empty:
        return [px.scatter(title="No Data").update_layout(template='plotly_white')]*3 + ["-"]*14 + [None, e_opts, e_val]

    target = clickData['points'][0]['customdata'][0] if clickData else None
    a_df = df_filtered[(df_filtered['Country']==target) & (df_filtered['Year'].dt.year>=y[0]) & (df_filtered['Year'].dt.year<=y[1])] if target else r_df

    
        ## --- bubble OR line chart depending on selection ---

    if g == "Country":
        c_df = r_df.dropna(subset=['GDP', 'CO2_Emissions', by]).sort_values("Year")

        if c_df.empty:
            fig_b = px.scatter(title="Insufficient data").update_layout(template="plotly_white")
        else:
            fig_b = px.scatter(
                c_df,
                x="Year",
                y=by,  # <-- dynamically use selected y-axis column here
                size="CO2_Emissions",
                color_discrete_sequence=["#298c8c"],
                hover_data={
                    "Year": True,
                    by: ":.2s",  # show formatted values for the selected y-axis
                    "CO2_Emissions": True
                },
                template="plotly_white"
            )
            fig_b.update_traces(
                marker=dict(
                    sizemode="area",
                    sizeref=2.*max(c_df["CO2_Emissions"])/(40.**2),
                    line=dict(width=1, color="white")
                )
            )
            fig_b.update_layout(
                xaxis_title="Year",
                yaxis_title=by.replace('_', ' ') + " (USD)" if by == "GDP" else by.replace('_', ' ')
            )

    else:
        # ----- BUBBLE CHART FOR MULTI-COUNTRY VIEW -----

        # aggregate by country
        b_df = r_df.groupby('Country', as_index=False).mean(numeric_only=True)

        # remove NaNs used by the chart
        b_df_plot = b_df.dropna(subset=['GDP', by, 'Life_Exp'])

        if b_df_plot.empty:
            fig_b = px.scatter(title="Insufficient data for bubble chart").update_layout(template='plotly_white')

        else:
            fig_b = px.scatter(
                b_df_plot,
                x='GDP',
                y=by,
                size='Life_Exp',
                color_discrete_sequence=['#298c8c'],
                hover_name='Country',
                custom_data=['Country'],
                log_x=True,
                template='plotly_white'
            )

            fig_b.update_traces(
                marker=dict(
                    sizemode='area',
                    sizeref=2.*max(b_df_plot['Life_Exp'])/(40.**2),
                    line=dict(width=1, color='white')
                )
            )

            fig_b.update_xaxes(
                tickformat=".1s",
                title="GDP (USD, Log Scale)"
            )

            fig_b.update_yaxes(
                type='log' if by != 'Elec_Access' else 'linear',
                title=by.replace('_', ' ')
            )
    # ---  line chart  ---
    def mk_line(df_in, y_v, col):
        d = df_in.dropna(subset=[y_v]).groupby('Year', as_index=False)[y_v].mean()
        if d.empty: return px.line().update_layout(template='plotly_white')
        return px.line(d, x='Year', y=y_v, markers=True, color_discrete_sequence=[col], template='plotly_white').update_layout(margin=dict(l=0,r=0,t=0,b=0))

    # --- KPI ---
    def get_kpi(col, is_m=False):
        temp = a_df.dropna(subset=[col])
        if temp.empty: return "-", "No data"
        ys = sorted(temp['Year'].unique())
        cur = temp[temp['Year']==ys[-1]][col].mean()
        txt = f"${cur/1e12:.1f}T" if is_m and cur>=1e12 else (f"${cur/1e9:.2f}B" if is_m else f"{cur:.1f}")
        sub = "Selected" if target else "Avg"
        if len(ys)>1:
            pre = temp[temp['Year']==ys[-2]][col].mean()
            if pre and pre != 0:
                diff = ((cur-pre)/pre)*100
                sub = html.Span(f"{diff:+.1f}% vs previous year", className="text-success" if diff>=0 else "text-danger")
        return txt, sub

    c2v, c2s = get_kpi('CO2_Emissions'); gdv, gds = get_kpi('GDP', True); ntv, nts = get_kpi('Nat_Res_Depletion')
    ifv, ifs = get_kpi('Inflation'); htv, hts = get_kpi('Life_Exp')
    
    # Regime Type 
    reg_df = a_df.dropna(subset=['Regime_Type'])
    reg = reg_df.sort_values('Year')['Regime_Type'].iloc[-1] if not reg_df.empty else "-"

    return fig_b, mk_line(a_df, ed, '#298c8c'), mk_line(a_df, sd, '#f1a226'), \
           f"REGIONAL OVERVIEW" if not target else f"FOCUS: {target}", \
           f"ECON: {target if target else e_val}", f"SOCIAL: {target if target else e_val}", \
           c2v, c2s, gdv, gds, ntv, nts, ifv, ifs, htv, hts, reg, clickData if trig != 'reset-btn' else None, e_opts, e_val

if __name__ == '__main__':
    app.run(debug=True, port=8050)