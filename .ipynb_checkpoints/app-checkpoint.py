import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
import os

# Optional: use pycountry if available for country -> ISO code conversion
try:
    import pycountry
except ImportError:
    pycountry = None


# =========================
# Data loading
# =========================
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    '..',
    'data',
    'raw',
    'WorldSustainabilityDataset.csv'
)

df = pd.read_csv(DATA_PATH)

# Clean/prepare columns
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
    'Income Classification (World Bank Definition)': 'Income_Group',
    'World Regions (UN SDG Definition)': 'SDG_Region'
}
df.rename(columns=col_mapping, inplace=True)

# Ensure required columns exist
required_cols = ['Year', 'Continent']
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Required column '{col}' not found in dataset.")

# Drop rows missing Continent/Year and make a safe copy
df_filtered = df.dropna(subset=['Continent', 'Year']).copy()

# Parse year safely
df_filtered['Year'] = pd.to_datetime(df_filtered['Year'].astype(str), format='%Y', errors='coerce')
df_filtered = df_filtered.dropna(subset=['Year']).copy()

# Convert likely numeric columns safely
numeric_cols = [
    'Elec_Access', 'GDP', 'CO2_Emissions', 'Life_Exp',
    'Women_Parliament', 'CO2_Damage_GNI', 'Nat_Res_Depletion', 'Inflation'
]
for col in numeric_cols:
    if col in df_filtered.columns:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')


# =========================
# Country flag helpers
# =========================
COUNTRY_ALIASES = {
    "United States": "US",
    "United States of America": "US",
    "UK": "GB",
    "United Kingdom": "GB",
    "Korea, Rep.": "KR",
    "Korea, Dem. People's Rep.": "KP",
    "South Korea": "KR",
    "North Korea": "KP",
    "Russian Federation": "RU",
    "Russia": "RU",
    "Viet Nam": "VN",
    "Iran, Islamic Rep.": "IR",
    "Egypt, Arab Rep.": "EG",
    "Syrian Arab Republic": "SY",
    "Yemen, Rep.": "YE",
    "Czech Republic": "CZ",
    "Slovak Republic": "SK",
    "Lao PDR": "LA",
    "Brunei Darussalam": "BN",
    "Congo, Dem. Rep.": "CD",
    "Congo, Rep.": "CG",
    "Gambia, The": "GM",
    "Bahamas, The": "BS",
    "Kyrgyz Republic": "KG",
    "Venezuela, RB": "VE",
    "Turkiye": "TR",
    "Turkey": "TR",
    "Taiwan, China": "TW",
    "Hong Kong SAR, China": "HK",
    "Macao SAR, China": "MO",
    "West Bank and Gaza": "PS",
    "Micronesia, Fed. Sts.": "FM",
    "St. Kitts and Nevis": "KN",
    "St. Lucia": "LC",
    "St. Vincent and the Grenadines": "VC",
    "Eswatini": "SZ",
}

def iso_to_flag(iso_code):
    """
    Convert ISO alpha-2 code to emoji flag.
    Example: 'CA' -> 🇨🇦
    """
    if not iso_code or len(iso_code) != 2:
        return ""
    iso_code = iso_code.upper()
    return chr(ord(iso_code[0]) + 127397) + chr(ord(iso_code[1]) + 127397)

def get_country_iso(country_name):
    """
    Best-effort conversion from country name to ISO alpha-2.
    """
    if not isinstance(country_name, str) or not country_name.strip():
        return None

    name = country_name.strip()

    if name in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[name]

    if pycountry is not None:
        # try exact lookup
        try:
            return pycountry.countries.lookup(name).alpha_2
        except Exception:
            pass

        # try common names / search fuzzy-like
        for country in pycountry.countries:
            if name.lower() in {
                getattr(country, 'name', '').lower(),
                getattr(country, 'official_name', '').lower(),
                getattr(country, 'common_name', '').lower()
            }:
                return country.alpha_2

    return None

def country_label_with_flag(country_name):
    iso = get_country_iso(country_name)
    flag = iso_to_flag(iso) if iso else ""
    return f"{flag} {country_name}" if flag else str(country_name)


# =========================
# Formatting helpers
# =========================
def is_missing(val):
    return pd.isna(val)

def format_compact_number(val, decimals=1):
    """
    Standardize numeric values into K/M/B.
    Missing values -> blank.
    """
    if is_missing(val):
        return ""

    abs_val = abs(val)

    if abs_val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.{decimals}f}B"
    elif abs_val >= 1_000_000:
        return f"{val / 1_000_000:.{decimals}f}M"
    elif abs_val >= 1_000:
        return f"{val / 1_000:.{decimals}f}K"
    else:
        return f"{val:.{decimals}f}"

def format_percent_or_number(val, decimals=1):
    """
    For % / ordinary metrics.
    Missing values -> blank.
    """
    if is_missing(val):
        return ""
    return f"{val:.{decimals}f}"

def vega_kmb_label_expr():
    """
    Vega expression for axis labels in K/M/B.
    """
    return (
        "datum.value == null ? '' : "
        "abs(datum.value) >= 1000000000 ? format(datum.value/1000000000, '.1f') + 'B' : "
        "abs(datum.value) >= 1000000 ? format(datum.value/1000000, '.1f') + 'M' : "
        "abs(datum.value) >= 1000 ? format(datum.value/1000, '.1f') + 'K' : "
        "format(datum.value, '.1f')"
    )

def add_formatted_tooltip_column(dataframe, y_col):
    temp = dataframe.copy()
    temp["FormattedValue"] = temp[y_col].apply(format_compact_number)
    return temp

def needs_compact_format(metric_name):
    """
    Metrics that should be shown in K/M/B format.
    """
    return metric_name in ['GDP', 'CO2_Emissions']


# =========================
# Dash app
# =========================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { 
                background-color: #f0f4f8; 
                font-family: 'Inter', sans-serif; 
                color: #334155;
            }
            .kpi-card { 
                background-color: #ffffff; 
                border-radius: 12px; 
                padding: 20px; 
                box-shadow: 0 4px 10px rgba(139, 92, 246, 0.15); 
                margin-bottom: 20px; 
                border: 2px solid #298c8c !important; 
                border-top: 6px solid #298c8c !important; 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .chart-card, .top-filter-card { 
                background-color: #ffffff; 
                border-radius: 16px; 
                padding: 20px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); 
                margin-bottom: 20px; 
                border: 1px solid rgba(226, 232, 240, 0.8); 
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .kpi-card:hover, .chart-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.2), 0 4px 6px -2px rgba(139, 92, 246, 0.1);
            }
            .chart-card { min-height: 400px; padding: 25px; }
            .top-filter-card { height: 100%; border-top: 4px solid #298c8c; border-radius: 12px; }
            
            .kpi-title { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; margin-bottom: 12px; }
            .kpi-value { 
                font-size: 2.2rem; 
                font-weight: 800; 
                color: #0f172a; 
                margin-bottom: 8px; 
                letter-spacing: -0.02em; 
            }
            .kpi-sub { font-size: 0.85rem; color: #64748b; font-weight: 600;}
            
            .kpi-positive { color: #10b981; font-weight: 600; padding: 2px 6px; background: rgba(16, 185, 129, 0.1); border-radius: 4px; }
            .kpi-negative { color: #ef4444; font-weight: 600; padding: 2px 6px; background: rgba(239, 68, 68, 0.1); border-radius: 4px;}
            
            .chart-title { font-size: 1.15rem; font-weight: 700; color: #1e293b; letter-spacing: -0.01em; }
            .dropdown-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 8px; letter-spacing: 0.05em;}
            
            .rc-slider-track, .dash-slider-range {
                background-color: #298c8c !important;
            }
            .rc-slider .rc-slider-handle, 
            .rc-slider .rc-slider-handle:active, 
            .rc-slider .rc-slider-handle:focus, 
            .rc-slider .rc-slider-handle:hover,
            .dash-slider-thumb,
            .dash-slider-thumb:active,
            .dash-slider-thumb:focus,
            .dash-slider-thumb:hover {
                border-color: #298c8c !important;
                background-color: #298c8c !important;
                box-shadow: none !important;
            }
            .rc-slider .rc-slider-handle-active:active,
            .dash-slider-thumb:active {
                box-shadow: 0 0 5px #298c8c !important;
            }
            .rc-slider-dot-active {
                border-color: #298c8c !important;
            }

            .Select-control { border-radius: 8px !important; border: 1px solid #cbd5e1 !important; box-shadow: none !important; }
            .Select-control:hover { border-color: #94a3b8 !important; }
            .has-value.Select--single > .Select-control .Select-value .Select-value-label,
            .has-value.is-pseudo-focused.Select--single > .Select-control .Select-value .Select-value-label {
                color: #0f172a !important;
                font-weight: 500;
            }
            
            .dashboard-title {
                text-align: center;
                padding: 10px 0 30px 0;
                font-size: 2.75rem;
                font-weight: 800;
                color: #0f172a;
                letter-spacing: -0.025em;
                text-transform: uppercase;
                border-bottom: 2px solid #298c8c;
                margin-bottom: 30px;
                display: flex;
                justify-content: center;
            }

            .empty-chart-note {
                display: flex;
                align-items: center;
                justify-content: center;
                width: 100%;
                height: 100%;
                color: #94a3b8;
                font-size: 1rem;
                font-weight: 600;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# =========================
# UI helpers
# =========================
def create_kpi(id_prefix, title):
    return html.Div(className='kpi-card', children=[
        html.Div(title, className='kpi-title'),
        html.H3(id=f'{id_prefix}-value', className='kpi-value', children=''),
        html.Div(id=f'{id_prefix}-sub', className='kpi-sub', children='')
    ])

def get_options_for_group(selected_group):
    if not selected_group or selected_group not in df_filtered.columns:
        return []

    values = df_filtered[selected_group].dropna().astype(str).unique().tolist()
    values.sort()

    if selected_group == 'Country':
        return [{'label': country_label_with_flag(v), 'value': v} for v in values]

    return [{'label': v, 'value': v} for v in values]


# =========================
# Layout
# =========================
app.layout = dbc.Container(fluid=True, className='p-4', children=[
    html.H1("Global Sustainability Tracker", className='dashboard-title'),

    dbc.Row(className='mb-4 align-items-stretch', children=[
        dbc.Col(md=6, children=[
            dbc.Row(className='h-100', children=[
                dbc.Col(width=4, children=[
                    html.Div(className='top-filter-card', children=[
                        html.Div("Group", className='dropdown-label'),
                        dcc.Dropdown(
                            id='group-dropdown',
                            options=[
                                {'label': 'Continent', 'value': 'Continent'},
                                {'label': 'Country', 'value': 'Country'},
                                {'label': 'Income Group', 'value': 'Income_Group'},
                                {'label': 'SDG Region', 'value': 'SDG_Region'}
                            ],
                            value='Continent',
                            clearable=False
                        )
                    ])
                ]),
                dbc.Col(width=4, children=[
                    html.Div(className='top-filter-card', children=[
                        html.Div("Selection", id='entity-dropdown-label', className='dropdown-label'),
                        dcc.Dropdown(
                            id='entity-dropdown',
                            options=get_options_for_group('Continent'),
                            value='Asia' if 'Asia' in df_filtered['Continent'].dropna().astype(str).unique().tolist()
                            else (sorted(df_filtered['Continent'].dropna().astype(str).unique().tolist())[0]
                                  if len(df_filtered['Continent'].dropna()) > 0 else None),
                            clearable=False
                        )
                    ])
                ]),
                dbc.Col(width=4, children=[
                    html.Div(className='top-filter-card', children=[
                        html.Div("Year Range", className='dropdown-label'),
                        dcc.RangeSlider(
                            id='year-slider',
                            min=int(df_filtered['Year'].dt.year.min()),
                            max=int(df_filtered['Year'].dt.year.max()),
                            value=[int(df_filtered['Year'].dt.year.min()), int(df_filtered['Year'].dt.year.max())],
                            step=1,
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ])
                ])
            ])
        ]),

        dbc.Col(md=6, children=[
            dbc.Row(children=[
                dbc.Col(width=4, children=create_kpi('kpi-co2', 'CO2 Emissions')),
                dbc.Col(width=4, children=create_kpi('kpi-gdp', 'GDP')),
                dbc.Col(width=4, children=create_kpi('kpi-natres', 'Natural Resources Depletion (%)'))
            ])
        ])
    ]),

    dbc.Row(children=[
        dbc.Col(md=6, children=[
            html.Div(className='chart-card', children=[
                dbc.Row(children=[
                    dbc.Col(html.Div("Environment Factors", className='chart-title'), width=8),
                    dbc.Col(dcc.Dropdown(
                        id='env-metric-dropdown',
                        options=[
                            {'label': 'CO2 Emissions', 'value': 'CO2_Emissions'},
                            {'label': 'CO2 Damage (% GNI)', 'value': 'CO2_Damage_GNI'},
                            {'label': 'Electricity Access', 'value': 'Elec_Access'}
                        ],
                        value='CO2_Emissions',
                        clearable=False
                    ), width=4)
                ]),
                html.Iframe(
                    id='env-chart',
                    style={'border': 'none', 'width': '100%', 'height': '450px', 'marginTop': '20px'}
                )
            ])
        ]),

        dbc.Col(md=4, children=[
            html.Div(className='chart-card', style={'minHeight': '260px'}, children=[
                dbc.Row(children=[
                    dbc.Col(html.Div("Economic Trackers", className='chart-title'), width=8),
                    dbc.Col(dcc.Dropdown(
                        id='econ-metric-dropdown',
                        options=[
                            {'label': 'GDP', 'value': 'GDP'},
                            {'label': 'Inflation', 'value': 'Inflation'}
                        ],
                        value='GDP',
                        clearable=False
                    ), width=4)
                ]),
                html.Iframe(
                    id='econ-chart',
                    style={'border': 'none', 'width': '100%', 'height': '200px', 'marginTop': '10px'}
                )
            ]),

            html.Div(className='chart-card', style={'minHeight': '260px'}, children=[
                dbc.Row(children=[
                    dbc.Col(html.Div("Social Progress", className='chart-title'), width=8),
                    dbc.Col(dcc.Dropdown(
                        id='sdg-metric-dropdown',
                        options=[
                            {'label': 'Life Expectancy', 'value': 'Life_Exp'},
                            {'label': 'Women in Parliament', 'value': 'Women_Parliament'}
                        ],
                        value='Women_Parliament',
                        clearable=False
                    ), width=4)
                ]),
                html.Iframe(
                    id='sdg-chart',
                    style={'border': 'none', 'width': '100%', 'height': '200px', 'marginTop': '10px'}
                )
            ])
        ]),

        dbc.Col(md=2, children=[
            create_kpi('kpi-inflation', 'Inflation (%)'),
            html.Div(className='kpi-card', children=[
                html.Div('Regime Type', className='kpi-title'),
                html.Div(id='kpi-regime-value', className='kpi-value', style={'fontSize': '1.3rem', 'marginBottom': '0px'})
            ]),
            create_kpi('kpi-women', 'Women Representation'),
            create_kpi('kpi-health', 'Health (Life Expectancy)')
        ])
    ])
])


# =========================
# Chart utility
# =========================
def empty_chart_html(message="No data available for this selection"):
    return f"""
    <html>
        <body style="margin:0;padding:0;font-family:Inter,sans-serif;background:#ffffff;">
            <div class="empty-chart-note" style="height:100vh;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-weight:600;">
                {message}
            </div>
        </body>
    </html>
    """

def get_line_chart(dataframe, y_col, color='#f1a226', height=200):
    """
    Handle missing data:
    - Drop NA in selected metric
    - If nothing remains, show blank-state chart
    Standardize numbers:
    - Use K/M/B in axis and tooltip for large metrics
    """
    if dataframe.empty or y_col not in dataframe.columns:
        return empty_chart_html()

    plot_df = dataframe[['Year', y_col]].dropna().copy()

    if plot_df.empty:
        return empty_chart_html("No non-missing values for this metric")

    agg_df = plot_df.groupby('Year', as_index=False)[y_col].mean()
    agg_df = agg_df.sort_values('Year').copy()

    if agg_df.empty:
        return empty_chart_html("No non-missing values for this metric")

    if needs_compact_format(y_col):
        agg_df = add_formatted_tooltip_column(agg_df, y_col)
        y_axis = alt.Axis(
            grid=True,
            gridColor='#f1f5f9',
            gridDash=[4, 4],
            labelColor='#64748b',
            domain=False,
            ticks=False,
            labelExpr=vega_kmb_label_expr()
        )
        tooltip_fields = [
            alt.Tooltip('Year:T', title='Year'),
            alt.Tooltip('FormattedValue:N', title='Value')
        ]
    else:
        agg_df['FormattedValue'] = agg_df[y_col].apply(lambda v: format_percent_or_number(v, 1))
        y_axis = alt.Axis(
            grid=True,
            gridColor='#f1f5f9',
            gridDash=[4, 4],
            labelColor='#64748b',
            domain=False,
            ticks=False,
            format='.1f'
        )
        tooltip_fields = [
            alt.Tooltip('Year:T', title='Year'),
            alt.Tooltip('FormattedValue:N', title='Value')
        ]

    chart = alt.Chart(agg_df).mark_line(
        point=alt.OverlayMarkDef(filled=True, fill='white', size=60, strokeWidth=2),
        strokeWidth=3,
        interpolate='monotone'
    ).encode(
        x=alt.X(
            'Year:T',
            title='',
            axis=alt.Axis(
                grid=False,
                labelColor='#64748b',
                domainColor='#e2e8f0',
                tickColor='#e2e8f0'
            )
        ),
        y=alt.Y(
            f'{y_col}:Q',
            title='',
            axis=y_axis
        ),
        color=alt.value(color),
        tooltip=tooltip_fields
    ).properties(
        width='container',
        height=height
    ).configure_view(
        strokeOpacity=0
    )

    return chart.to_html()


# =========================
# Callbacks
# =========================
@app.callback(
    [Output('entity-dropdown-label', 'children'),
     Output('entity-dropdown', 'options'),
     Output('entity-dropdown', 'value')],
    Input('group-dropdown', 'value')
)
def update_entity_options(selected_group):
    if not selected_group or selected_group not in df_filtered.columns:
        return "Selection", [], None

    label_map = {
        'Continent': 'Continent',
        'Country': 'Country',
        'Income_Group': 'Income Group',
        'SDG_Region': 'SDG Region'
    }

    options = get_options_for_group(selected_group)
    label = label_map.get(selected_group, "Selection")
    value = options[0]['value'] if options else None

    return label, options, value


@app.callback(
    [
        Output('env-chart', 'srcDoc'),
        Output('econ-chart', 'srcDoc'),
        Output('sdg-chart', 'srcDoc'),
        Output('kpi-co2-value', 'children'), Output('kpi-co2-sub', 'children'),
        Output('kpi-gdp-value', 'children'), Output('kpi-gdp-sub', 'children'),
        Output('kpi-natres-value', 'children'), Output('kpi-natres-sub', 'children'),
        Output('kpi-inflation-value', 'children'), Output('kpi-inflation-sub', 'children'),
        Output('kpi-women-value', 'children'), Output('kpi-women-sub', 'children'),
        Output('kpi-health-value', 'children'), Output('kpi-health-sub', 'children'),
        Output('kpi-regime-value', 'children')
    ],
    [
        Input('group-dropdown', 'value'),
        Input('entity-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('env-metric-dropdown', 'value'),
        Input('econ-metric-dropdown', 'value'),
        Input('sdg-metric-dropdown', 'value')
    ]
)
def update_dashboard(group, entity, year_range, env_metric, econ_metric, sdg_metric):
    blank = ""

    if not group or not entity or group not in df_filtered.columns or not year_range:
        return (
            empty_chart_html(), empty_chart_html(), empty_chart_html(),
            blank, blank, blank, blank, blank, blank,
            blank, blank, blank, blank, blank, blank, blank
        )

    filtered = df_filtered[
        (df_filtered[group].astype(str) == str(entity)) &
        (df_filtered['Year'].dt.year >= year_range[0]) &
        (df_filtered['Year'].dt.year <= year_range[1])
    ].copy()

    env_html = get_line_chart(filtered, env_metric, '#f1a226', 400)
    econ_html = get_line_chart(filtered, econ_metric, '#f1a226', 180)
    sdg_html = get_line_chart(filtered, sdg_metric, '#f1a226', 180)

    if filtered.empty:
        return (
            env_html, econ_html, sdg_html,
            blank, blank, blank, blank, blank, blank,
            blank, blank, blank, blank, blank, blank, blank
        )

    years = sorted(filtered['Year'].dropna().unique())
    if len(years) < 2:
        return (
            env_html, econ_html, sdg_html,
            blank, blank, blank, blank, blank, blank,
            blank, blank, blank, blank, blank, blank, blank
        )

    y_curr = years[-1]
    y_prev = years[-2]

    c_df = filtered[filtered['Year'] == y_curr].copy()
    p_df = filtered[filtered['Year'] == y_prev].copy()

    def calc_kpi(col, formatter=format_percent_or_number):
        if col not in filtered.columns:
            return blank, blank

        curr = c_df[col].mean(skipna=True)
        prev = p_df[col].mean(skipna=True)

        # Requirement c: blanks for missing data
        if pd.isna(curr):
            return blank, blank

        curr_display = formatter(curr)

        # if previous missing or zero, show current only, blank comparison
        if pd.isna(prev) or prev == 0:
            return curr_display, blank

        pct = ((curr - prev) / prev) * 100
        sign = "+" if pct >= 0 else ""
        color_class = "kpi-positive" if pct >= 0 else "kpi-negative"

        sub = html.Span([
            f"vs prev {formatter(prev)} (",
            html.Span(f"{sign}{pct:.1f}%", className=color_class),
            ")"
        ])
        return curr_display, sub

    co2_v, co2_s = calc_kpi('CO2_Emissions', format_compact_number)
    gdp_v, gdp_s = calc_kpi('GDP', format_compact_number)
    natres_v, natres_s = calc_kpi('Nat_Res_Depletion', format_percent_or_number)
    inf_v, inf_s = calc_kpi('Inflation', format_percent_or_number)
    wom_v, wom_s = calc_kpi('Women_Parliament', format_percent_or_number)
    hlt_v, hlth_s = calc_kpi('Life_Exp', format_percent_or_number)

    regime = blank
    if 'Regime_Type' in c_df.columns:
        regime_series = c_df['Regime_Type'].dropna()
        if not regime_series.empty:
            regime = regime_series.mode().iloc[0]

    return (
        env_html, econ_html, sdg_html,
        co2_v, co2_s,
        gdp_v, gdp_s,
        natres_v, natres_s,
        inf_v, inf_s,
        wom_v, wom_s,
        hlt_v, hlth_s,
        regime
    )


if __name__ == '__main__':
    app.run(debug=True, port=8050)
