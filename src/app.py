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

LABEL_MAP = {
    'GDP': 'GDP (USD)',
    'Inflation': 'Inflation (%)',
    'Life_Exp': 'Life Expectancy (Years)',
    'Women_Parliament': 'Women in Parliament (%)',
    'CO2_Emissions': 'CO2 Emissions (M Tonnes)',
    'CO2_Damage_GNI': 'CO2 Damage (% GNI)',
    'Elec_Access': 'Electricity Access (%)',
    'Nat_Res_Depletion': 'Nat. Res. Depletion (% GNI)',
}

COUNTRY_TO_ISO = {
    "Afghanistan": "AF", "Albania": "AL", "Algeria": "DZ", "Angola": "AO",
    "Antigua and Barbuda": "AG", "Argentina": "AR", "Armenia": "AM", "Australia": "AU",
    "Austria": "AT", "Azerbaijan": "AZ", "Bahamas": "BS", "Bahamas, The": "BS",
    "Bahrain": "BH", "Bangladesh": "BD", "Barbados": "BB", "Belarus": "BY",
    "Belgium": "BE", "Belize": "BZ", "Benin": "BJ", "Bhutan": "BT",
    "Bolivia": "BO", "Bosnia and Herzegovina": "BA", "Botswana": "BW",
    "Brazil": "BR", "Brunei": "BN", "Brunei Darussalam": "BN", "Bulgaria": "BG",
    "Burkina Faso": "BF", "Burundi": "BI", "Cambodia": "KH", "Cameroon": "CM",
    "Canada": "CA", "Cape Verde": "CV", "Central African Republic": "CF", "Chad": "TD",
    "Chile": "CL", "China": "CN", "Colombia": "CO", "Comoros": "KM",
    "Congo, Dem. Rep.": "CD", "Congo, Rep.": "CG", "Costa Rica": "CR",
    "Cote d'Ivoire": "CI", "Croatia": "HR", "Cuba": "CU", "Cyprus": "CY",
    "Czech Republic": "CZ", "Czechia": "CZ", "Denmark": "DK", "Djibouti": "DJ",
    "Dominica": "DM", "Dominican Republic": "DO", "Ecuador": "EC", "Egypt": "EG",
    "Egypt, Arab Rep.": "EG", "El Salvador": "SV", "Equatorial Guinea": "GQ",
    "Eritrea": "ER", "Estonia": "EE", "Eswatini": "SZ", "Ethiopia": "ET",
    "Fiji": "FJ", "Finland": "FI", "France": "FR", "Gabon": "GA",
    "Gambia": "GM", "Gambia, The": "GM", "Georgia": "GE", "Germany": "DE",
    "Ghana": "GH", "Greece": "GR", "Grenada": "GD", "Guatemala": "GT",
    "Guinea": "GN", "Guinea-Bissau": "GW", "Guyana": "GY", "Haiti": "HT",
    "Honduras": "HN", "Hungary": "HU", "Iceland": "IS", "India": "IN",
    "Indonesia": "ID", "Iran": "IR", "Iran, Islamic Rep.": "IR", "Iraq": "IQ",
    "Ireland": "IE", "Israel": "IL", "Italy": "IT", "Jamaica": "JM",
    "Japan": "JP", "Jordan": "JO", "Kazakhstan": "KZ", "Kenya": "KE",
    "Kiribati": "KI", "Korea, Dem. People's Rep.": "KP", "Korea, Rep.": "KR",
    "Kosovo": "XK", "Kuwait": "KW", "Kyrgyz Republic": "KG", "Kyrgyzstan": "KG",
    "Lao PDR": "LA", "Laos": "LA", "Latvia": "LV", "Lebanon": "LB",
    "Lesotho": "LS", "Liberia": "LR", "Libya": "LY", "Lithuania": "LT",
    "Luxembourg": "LU", "Madagascar": "MG", "Malawi": "MW", "Malaysia": "MY",
    "Maldives": "MV", "Mali": "ML", "Malta": "MT", "Marshall Islands": "MH",
    "Mauritania": "MR", "Mauritius": "MU", "Mexico": "MX", "Micronesia, Fed. Sts.": "FM",
    "Moldova": "MD", "Mongolia": "MN", "Montenegro": "ME", "Morocco": "MA",
    "Mozambique": "MZ", "Myanmar": "MM", "Namibia": "NA", "Nepal": "NP",
    "Netherlands": "NL", "New Zealand": "NZ", "Nicaragua": "NI", "Niger": "NE",
    "Nigeria": "NG", "North Macedonia": "MK", "Norway": "NO", "Oman": "OM",
    "Pakistan": "PK", "Panama": "PA", "Papua New Guinea": "PG", "Paraguay": "PY",
    "Peru": "PE", "Philippines": "PH", "Poland": "PL", "Portugal": "PT",
    "Qatar": "QA", "Romania": "RO", "Russian Federation": "RU", "Russia": "RU",
    "Rwanda": "RW", "Samoa": "WS", "Sao Tome and Principe": "ST", "Saudi Arabia": "SA",
    "Senegal": "SN", "Serbia": "RS", "Seychelles": "SC", "Sierra Leone": "SL",
    "Singapore": "SG", "Slovak Republic": "SK", "Slovakia": "SK", "Slovenia": "SI",
    "Solomon Islands": "SB", "Somalia": "SO", "South Africa": "ZA", "South Sudan": "SS",
    "Spain": "ES", "Sri Lanka": "LK", "St. Kitts and Nevis": "KN", "St. Lucia": "LC",
    "St. Vincent and the Grenadines": "VC", "Sudan": "SD", "Suriname": "SR",
    "Sweden": "SE", "Switzerland": "CH", "Syrian Arab Republic": "SY", "Syria": "SY",
    "Tajikistan": "TJ", "Tanzania": "TZ", "Thailand": "TH", "Timor-Leste": "TL",
    "Togo": "TG", "Tonga": "TO", "Trinidad and Tobago": "TT", "Tunisia": "TN",
    "Turkey": "TR", "Turkiye": "TR", "Turkmenistan": "TM", "Tuvalu": "TV",
    "Uganda": "UG", "Ukraine": "UA", "United Arab Emirates": "AE",
    "United Kingdom": "GB", "UK": "GB",
    "United States": "US", "United States of America": "US",
    "Uruguay": "UY", "Uzbekistan": "UZ", "Vanuatu": "VU", "Venezuela": "VE",
    "Venezuela, RB": "VE", "Viet Nam": "VN", "Vietnam": "VN", "Yemen": "YE",
    "Yemen, Rep.": "YE", "Zambia": "ZM", "Zimbabwe": "ZW"
}

def iso_to_flag(iso_code):
    if not iso_code or len(iso_code) != 2:
        return ""
    iso_code = iso_code.upper()
    return chr(ord(iso_code[0]) + 127397) + chr(ord(iso_code[1]) + 127397)

def country_label_with_flag(country_name):
    iso = COUNTRY_TO_ISO.get(str(country_name).strip(), "")
    flag = iso_to_flag(iso) if iso else "🌍"
    return f"{flag} {country_name}"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}<title>Global Sustainability Tracker</title>{%css%}
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
    """
    Creates a standardized KPI card component with a title, tooltip, and placeholders for value and subtext.

    Args:
        id_prefix (str): Prefix used for the IDs of the internal components (value and subtext).
        title (str): The display title for the KPI card.
        tooltip (str, optional): Explanatory text to display when hovering over the info icon. Defaults to "".

    Returns:
        html.Div: A Dash HTML Div component representing the layout of the KPI card.
    """
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
                dcc.Link("Multi-Country Comparison", href="/compare", className="nav-link"),
            ])
        ]),
        html.Div(id='page-content')
    ], fluid=True, className="px-4")
])

def layout_main():
    """
    Defines the layout for the main dashboard view, including global KPIs, drop-down filters, 
    a scatter plot (bubble chart), and track-specific line charts (economic/social).

    Returns:
        html.Div: A Dash HTML Div holding all the layout components for the main page.
    """
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
    'CO2 (M Tonnes)',
    tooltip="Measures carbon dioxide emissions generated annually. Higher values indicate greater negative environmental impact."
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
                    'LIFE EXP (YEARS)',
                    tooltip="Life expectancy indicates the average number of years a newborn is expected to live if current mortality patterns continue. It is a key indicator of overall population health, healthcare access, and living conditions. This is the most recent value available (2018)."
                )
            ])
        ])
    ])

def layout_compare():
    """
    Defines the layout for the multi-country comparison view, featuring dropdowns to 
    select two specific countries and a key performance indicator (KPI) metric, 
    along with a single line chart for direct trend comparison.

    Returns:
        html.Div: A Dash HTML Div containing the dropdowns and the comparison chart.
    """
    c_opts = [{'label': country_label_with_flag(c), 'value': c} for c in sorted(df_filtered['Country'].unique())]
    k_opts = [{'label': v, 'value': k} for k, v in LABEL_MAP.items()]
    return html.Div([
        dbc.Row([
            dbc.Col(md=12, children=[
                html.Div(className='chart-card mb-4', children=[
                    html.Div("COUNTRY COMPARISON", className='kpi-title'),
                    dbc.Row([
                        dbc.Col(md=4, children=[html.Div("COUNTRY 1", className='kpi-title'), dcc.Dropdown(id='compare-c1', options=c_opts, value='Canada', clearable=False)]),
                        dbc.Col(md=4, children=[html.Div("COUNTRY 2", className='kpi-title'), dcc.Dropdown(id='compare-c2', options=c_opts, value='China', clearable=False)]),
                        dbc.Col(md=4, children=[html.Div("KPI", className='kpi-title'), dcc.Dropdown(id='compare-kpi', options=k_opts, value='GDP', clearable=False)])
                    ])
                ])
            ])
        ]),
        dbc.Row([
            dbc.Col(md=12, children=[
                html.Div(className='chart-card', children=[
                    html.Div(id='compare-chart-title', className='fw-bold mb-2'),
                    dcc.Graph(id='compare-chart')
                ])
            ])
        ])
    ])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(p):
    """
    Routes the user to the appropriate page layout based on the current URL pathname.

    Args:
        p (str): The current URL pathname (e.g., '/' or '/compare').

    Returns:
        html.Div: The layout component for the requested page.
    """
    return layout_compare() if p == '/compare' else layout_main()

@app.callback(
    [Output('compare-chart', 'figure'), Output('compare-chart-title', 'children')],
    [Input('compare-c1', 'value'), Input('compare-c2', 'value'), Input('compare-kpi', 'value')]
)
def update_comp(c1, c2, kpi):
    """
    Updates the multi-country comparison chart and its title based on user selections.

    Args:
        c1 (str): The name of the first selected country.
        c2 (str): The name of the second selected country.
        kpi (str): The selected KPI column name from the dataset.

    Returns:
        tuple (plotly.graph_objs._figure.Figure, str): 
            - The configured Plotly line chart figure comparing the two countries.
            - The dynamic title for the comparison chart.
    """
    f = df_filtered[df_filtered['Country'].isin([c1, c2])]
    fig = px.line(f, x='Year', y=kpi, color='Country', markers=True, template='plotly_white')
    fig.update_layout(yaxis_title=LABEL_MAP.get(kpi))
    return fig, f"{LABEL_MAP.get(kpi)}: {c1} vs {c2}"

@app.callback(
    [Output("bubble-y-drop", "options"),
     Output("bubble-y-drop", "value")],
    Input("group-dropdown", "value")
)
def update_bubble_dropdown(group):
    """
    Dynamically updates the available options for the bubble chart's Y-axis dropdown 
    based on the currently selected grouping level (e.g., 'Country' vs 'Continent').

    Args:
        group (str): The selected grouping column.

    Returns:
        tuple (list, str): 
            - A list of dictionary options representing valid Y-axis metrics.
            - The default selected metric based on the group type.
    """
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
    """
    Main dashboard callback. Updates all charts, KPIs, and related titles based on user interactions 
    with the filters, slider, and the bubble chart itself (cross-filtering).

    Args:
        g (str): Group-level selection (e.g., 'Continent', 'Country').
        e (str): Specific entity selection within the group (e.g., 'Asia', 'Canada').
        y (list[int]): Two-element list representing the [start, end] years from the range slider.
        by (str): Selected Y-axis metric for the bubble chart.
        ed (str): Selected Y-axis metric for the economic line chart.
        sd (str): Selected Y-axis metric for the social progress line chart.
        clickData (dict | None): Data payload from cliking a point on the bubble chart. Used for drill-down.
        n_clicks (int | None): Number of times the "Reset" button has been clicked.
        path (str): Current URL path to prevent execution on non-main pages.

    Returns:
        tuple: A massive 20-element tuple containing updated dash component properties (figures, text strings, dropdown states).
    """
    if path != '/': return [dash.no_update]*20
    ctx = dash.callback_context
    trig = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    opt_vals = sorted(df_filtered[g].dropna().unique())
    e_opts = [{'label': country_label_with_flag(i) if g == 'Country' else i, 'value': i} for i in opt_vals]
    e_val = e if e in opt_vals else opt_vals[0]
    
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
    def mk_line(df_in, y_v, col, y_label=None):
        """
        Helper function to generate a standardized Plotly line chart.

        Args:
            df_in (pd.DataFrame): The filtered dataset to plot.
            y_v (str): The column name to plot on the Y-axis.
            col (str): Hex color code for the line trace.
            y_label (str, optional): Human-readable label for the Y-axis. If None, uses `y_v`.

        Returns:
            plotly.graph_objs._figure.Figure: The generated line chart figure object.
        """
        d = df_in.dropna(subset=[y_v]).groupby('Year', as_index=False)[y_v].mean()
        if d.empty: return px.line().update_layout(template='plotly_white')
        fig = px.line(d, x='Year', y=y_v, markers=True, color_discrete_sequence=[col], template='plotly_white')
        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), yaxis_title=y_label or y_v)
        return fig

    # --- KPI ---
    def get_kpi(col, is_m=False, invert_color=False):
        """
        Calculates the most recent metric value and its percentage change from the previous available year.
        Formats the output text with appropriate scaling (e.g., Billions/Trillions) and colored indicators.

        Args:
            col (str): Dataset column name representing the metric to calculate.
            is_m (bool, optional): If True, formats large numbers into Billions ('B') or Trillions ('T'). Defaults to False.
            invert_color (bool, optional): If True, a positive change is colored dangerously (red) and negative
                                           is colored successfully (green), standardizing "loss is better" metrics like CO2. Defaults to False.

        Returns:
            tuple (str, dash.html.Span | str): The formatted current value, and a styled HTML span showing the % change or context.
        """
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
                color_class = ("text-danger" if diff>=0 else "text-success") if invert_color else ("text-success" if diff>=0 else "text-danger")
                sub = html.Span(f"{diff:+.1f}% vs previous year", className=color_class)
        return txt, sub

    c2v, c2s = get_kpi('CO2_Emissions', invert_color=True)
    gdv, gds = get_kpi('GDP', is_m=True)
    ntv, nts = get_kpi('Nat_Res_Depletion', invert_color=True)
    ifv, ifs = get_kpi('Inflation', invert_color=True)
    htv, hts = get_kpi('Life_Exp')
    
    # Regime Type 
    reg_df = a_df.dropna(subset=['Regime_Type'])
    reg = reg_df.sort_values('Year')['Regime_Type'].iloc[-1] if not reg_df.empty else "-"

    return fig_b, mk_line(a_df, ed, '#f1a226', LABEL_MAP.get(ed)), mk_line(a_df, sd, '#f1a226', LABEL_MAP.get(sd)), \
           f"REGIONAL OVERVIEW" if not target else f"FOCUS: {target}", \
           f"Economic Trackers", f"Social Progress", \
           c2v, c2s, gdv, gds, ntv, nts, ifv, ifs, htv, hts, reg, clickData if trig != 'reset-btn' else None, e_opts, e_val

if __name__ == '__main__':
    app.run(debug=True, port=8050)