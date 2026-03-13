import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import altair as alt
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), 'WorldSustainabilityDataset.csv')
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
    'Income Classification (World Bank Definition)': 'Income_Group',
    'World Regions (UN SDG Definition)': 'SDG_Region'
}
df.rename(columns=col_mapping, inplace=True)

required_cols = ['Year', 'Continent', 'Country']
for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"Required column '{col}' not found in dataset.")

df_filtered = df.dropna(subset=['Continent', 'Year', 'Country']).copy()
df_filtered['Year'] = pd.to_datetime(df_filtered['Year'].astype(str), format='%Y', errors='coerce')
df_filtered = df_filtered.dropna(subset=['Year']).copy()
# After reading the data, convert numeric columns to numeric for safety and NaN for errors.
numeric_cols = [
    'Elec_Access', 'GDP', 'CO2_Emissions', 'Life_Exp',
    'Women_Parliament', 'CO2_Damage_GNI', 'Nat_Res_Depletion', 'Inflation'
]
for col in numeric_cols:
    if col in df_filtered.columns:
        df_filtered[col] = pd.to_numeric(df_filtered[col], errors='coerce')

YEAR_MIN = int(df_filtered['Year'].dt.year.min())
YEAR_MAX = int(df_filtered['Year'].dt.year.max())

# This entire dictionary is for mapping country names to flag codes.
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
# Convert ISO codes to national flag emojis
def iso_to_flag(iso_code):
    if not iso_code or len(iso_code) != 2:
        return ""
    iso_code = iso_code.upper()
    return chr(ord(iso_code[0]) + 127397) + chr(ord(iso_code[1]) + 127397)
# Combine "national flag + country name" into the tags displayed in the selector.
def country_label_with_flag(country_name):
    iso = COUNTRY_TO_ISO.get(str(country_name).strip(), "")
    flag = iso_to_flag(iso) if iso else "🌍"
    return f"{flag} {country_name}"
# Use a label with the national flag in the Country dropdown options.
def get_options_for_group(selected_group):
    if not selected_group or selected_group not in df_filtered.columns:
        return []
    values = sorted(df_filtered[selected_group].dropna().astype(str).unique().tolist())
    if selected_group == 'Country':
        return [{'label': country_label_with_flag(v), 'value': v} for v in values]
    return [{'label': v, 'value': v} for v in values]

def get_select_options_for_group(selected_group):
    return get_options_for_group(selected_group)
# Plain number format
def format_plain(val, decimals=1):
    if pd.isna(val):
        return ""
    return f"{val:.{decimals}f}"
# CO2 format(million tonnes)
def format_co2(val, decimals=1):
    if pd.isna(val):
        return ""
    return f"{val:.{decimals}f}M"
# Larger values ​​such as GDP are standardized to K/M/B/T
def format_kmbt(val, decimals=1):
    if pd.isna(val):
        return ""
    abs_val = abs(val)
    if abs_val >= 1_000_000_000_000:
        return f"{val / 1_000_000_000_000:.{decimals}f}T"
    elif abs_val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.{decimals}f}B"
    elif abs_val >= 1_000_000:
        return f"{val / 1_000_000:.{decimals}f}M"
    elif abs_val >= 1_000:
        return f"{val / 1_000:.{decimals}f}K"
    return f"{val:.{decimals}f}"
# Select the corresponding format based on the indicator (GDP→format_kmbt and CO2→format_co2).
def get_metric_formatter(metric_name):
    if metric_name == 'GDP':
        return format_kmbt
    elif metric_name == 'CO2_Emissions':
        return format_co2
    return format_plain
# The y-axis of the chart also uniformly displays K/M/B/T.
def vega_label_expr_for_metric(metric_name):
    if metric_name == 'GDP':
        return (
            "datum.value == null ? '' : "
            "abs(datum.value) >= 1000000000000 ? format(datum.value/1000000000000, '.1f') + 'T' : "
            "abs(datum.value) >= 1000000000 ? format(datum.value/1000000000, '.1f') + 'B' : "
            "abs(datum.value) >= 1000000 ? format(datum.value/1000000, '.1f') + 'M' : "
            "abs(datum.value) >= 1000 ? format(datum.value/1000, '.1f') + 'K' : "
            "format(datum.value, '.1f')"
        )
    elif metric_name == 'CO2_Emissions':
        return "datum.value == null ? '' : format(datum.value, '.1f') + 'M'"
    return "datum.value == null ? '' : format(datum.value, '.1f')"

def slider_label_style(value, min_year, max_year, side="left"):
    pct = 50 if max_year == min_year else ((value - min_year) / (max_year - min_year)) * 100
    offset = 12 if side == "left" else 30
    return {"left": f"calc({pct}% - {offset}px)"}

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
    <style>
        body {
            background-color: #f0f4f8;
            font-family: Arial, Helvetica, sans-serif;
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
        }

        .chart-card, .top-filter-card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            margin-bottom: 20px;
            border: 1px solid rgba(226, 232, 240, 0.8);
        }

        .chart-card { min-height: 400px; padding: 25px; }
        .top-filter-card { height: 100%; border-top: 4px solid #298c8c; border-radius: 12px; }

        .kpi-title {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #475569;
            margin-bottom: 12px;
        }

        .kpi-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .kpi-sub { font-size: 0.85rem; color: #64748b; font-weight: 600; }
        .kpi-positive { color: #10b981; font-weight: 600; padding: 2px 6px; background: rgba(16, 185, 129, 0.1); border-radius: 4px; }
        .kpi-negative { color: #ef4444; font-weight: 600; padding: 2px 6px; background: rgba(239, 68, 68, 0.1); border-radius: 4px; }
        .chart-title { font-size: 1.15rem; font-weight: 700; color: #1e293b; letter-spacing: -0.01em; }
        .dropdown-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 8px; letter-spacing: 0.05em; }

        .rc-slider-track, .dash-slider-range { background-color: #298c8c !important; }
        .rc-slider .rc-slider-handle,
        .rc-slider .rc-slider-handle:active,
        .rc-slider .rc-slider-handle:focus,
        .rc-slider .rc-slider-handle:hover {
            border-color: #298c8c !important;
            background-color: #298c8c !important;
            box-shadow: none !important;
        }

        .native-select {
            height: 54px;
            border-radius: 16px !important;
            border: 2px solid #b8c2d9 !important;
            font-size: 18px !important;
            font-weight: 800 !important;
            color: #24324a !important;
            padding-left: 18px !important;
            box-shadow: none !important;
        }

        .chart-metric-select {
            height: 56px !important;
            border-radius: 12px !important;
            border: 2px solid #b8c2d9 !important;
            background-color: #ffffff !important;
            box-shadow: none !important;
            font-size: 16px !important;
            font-weight: 800 !important;
            color: #24324a !important;
            font-family: Arial, Helvetica, sans-serif !important;
            padding-left: 14px !important;
            padding-right: 42px !important;
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

        .year-slider-wrapper {
            position: relative;
            padding-top: 10px;
            padding-bottom: 38px;
        }

        .year-label-layer {
            position: relative;
            width: 100%;
            height: 0;
        }

        .year-value-box {
            position: absolute;
            top: 0px;
            transform: translateX(0);
            background-color: #6b6b6b;
            color: white;
            border-radius: 10px;
            width: 42px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 500;
            font-size: 0.7rem;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.16);
            pointer-events: none;
            transition: left 0.01s linear;
            font-variant-numeric: tabular-nums;
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

def create_kpi(id_prefix, title):
    return html.Div(className='kpi-card', children=[
        html.Div(title, className='kpi-title'),
        html.H3(id=f'{id_prefix}-value', className='kpi-value', children=''),
        html.Div(id=f'{id_prefix}-sub', className='kpi-sub', children='')
    ])

app.layout = dbc.Container(fluid=True, className='p-4', children=[
    html.H1("Global Sustainability Tracker", className='dashboard-title'),

    dbc.Row(className='mb-4 align-items-stretch', children=[
        dbc.Col(md=6, children=[
            dbc.Row(className='h-100', children=[
                dbc.Col(width=4, children=[
                    html.Div(className='top-filter-card', children=[
                        html.Div("Group", className='dropdown-label'),
                        dbc.Select(
                            id='group-dropdown',
                            className='native-select',
                            options=[
                                {'label': 'Continent', 'value': 'Continent'},
                                {'label': 'Country', 'value': 'Country'},
                                {'label': 'Income Group', 'value': 'Income_Group'},
                                {'label': 'SDG Region', 'value': 'SDG_Region'}
                            ],
                            value='Continent'
                        )
                    ])
                ]),
                dbc.Col(width=4, children=[
                    html.Div(className='top-filter-card', children=[
                        html.Div("Selection", id='entity-dropdown-label', className='dropdown-label'),
                        # This makes the dropdown actually use the options with the flag shown above.
                        dbc.Select(
                            id='entity-dropdown',
                            className='native-select',
                            options=get_select_options_for_group('Continent'),
                            value='Asia' if 'Asia' in df_filtered['Continent'].dropna().astype(str).unique().tolist()
                            else sorted(df_filtered['Continent'].dropna().astype(str).unique().tolist())[0]
                        )
                    ])
                ]),
                dbc.Col(width=4, children=[
                    html.Div(className='top-filter-card', children=[
                        html.Div("Year Range", className='dropdown-label'),
                        html.Div(className='year-slider-wrapper', children=[
                            dcc.RangeSlider(
                                id='year-slider',
                                min=YEAR_MIN,
                                max=YEAR_MAX,
                                value=[YEAR_MIN, YEAR_MAX],
                                step=1,
                                marks=None
                            ),
                            html.Div(className='year-label-layer', children=[
                                html.Div(id='year-start-label', className='year-value-box'),
                                html.Div(id='year-end-label', className='year-value-box')
                            ])
                        ])
                    ])
                ])
            ])
        ]),
        dbc.Col(md=6, children=[
            dbc.Row(children=[
                dbc.Col(width=4, children=create_kpi('kpi-co2', 'CO2 Emissions (MILLION TONNES)')),
                dbc.Col(width=4, children=create_kpi('kpi-gdp', 'GDP (USD)')),
                dbc.Col(width=4, children=create_kpi('kpi-natres', 'Natural Resources Depletion (%)'))
            ])
        ])
    ]),

    dbc.Row(children=[
        dbc.Col(md=6, children=[
            html.Div(className='chart-card', children=[
                dbc.Row(children=[
                    dbc.Col(html.Div("Environment Factors", className='chart-title'), width=8),
                    dbc.Col(
                        dbc.Select(
                            id='env-metric-dropdown',
                            className='chart-metric-select',
                            options=[
                                {'label': 'CO2 Emissions (MILLION TONNES)', 'value': 'CO2_Emissions'},
                                {'label': 'CO2 Damage (% GNI)', 'value': 'CO2_Damage_GNI'},
                                {'label': 'Electricity Access', 'value': 'Elec_Access'}
                            ],
                            value='CO2_Emissions'
                        ),
                        width=4
                    )
                ]),
                html.Iframe(id='env-chart', style={'border': 'none', 'width': '100%', 'height': '450px', 'marginTop': '20px'})
            ])
        ]),

        dbc.Col(md=4, children=[
            html.Div(className='chart-card', style={'minHeight': '260px'}, children=[
                dbc.Row(children=[
                    dbc.Col(html.Div("Economic Trackers", className='chart-title'), width=8),
                    dbc.Col(
                        dbc.Select(
                            id='econ-metric-dropdown',
                            className='chart-metric-select',
                            options=[
                                {'label': 'GDP (USD)', 'value': 'GDP'},
                                {'label': 'Inflation', 'value': 'Inflation'}
                            ],
                            value='GDP'
                        ),
                        width=4
                    )
                ]),
                html.Iframe(id='econ-chart', style={'border': 'none', 'width': '100%', 'height': '200px', 'marginTop': '10px'})
            ]),

            html.Div(className='chart-card', style={'minHeight': '260px'}, children=[
                dbc.Row(children=[
                    dbc.Col(html.Div("Social Progress", className='chart-title'), width=8),
                    dbc.Col(
                        dbc.Select(
                            id='sdg-metric-dropdown',
                            className='chart-metric-select',
                            options=[
                                {'label': 'Life Expectancy', 'value': 'Life_Exp'},
                                {'label': 'Women in Parliament', 'value': 'Women_Parliament'}
                            ],
                            value='Women_Parliament'
                        ),
                        width=4
                    )
                ]),
                html.Iframe(id='sdg-chart', style={'border': 'none', 'width': '100%', 'height': '200px', 'marginTop': '10px'})
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

def empty_chart_html(message="No data available for this selection"):
    return f"""
    <html>
        <body style="margin:0;padding:0;font-family:Arial, Helvetica, sans-serif;background:#ffffff;">
            <div style="height:100vh;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-weight:600;">
                {message}
            </div>
        </body>
    </html>
    """

def get_line_chart(dataframe, y_col, color='#f1a226', height=200):
    # If the entire dataframe is empty, an empty message will also be displayed.
    if dataframe.empty or y_col not in dataframe.columns:
        return empty_chart_html()
    # To avoid chart errors due to null values
    plot_df = dataframe[['Year', y_col]].dropna().copy()
    # If this column is completely missing, an empty chart will be displayed.
    if plot_df.empty:
        return empty_chart_html("No non-missing values for this metric")

    agg_df = plot_df.groupby('Year', as_index=False)[y_col].mean().sort_values('Year').copy()
    # The standardized values ​​were also used in the chart tooltip.
    formatter = get_metric_formatter(y_col)
    agg_df['FormattedValue'] = agg_df[y_col].apply(formatter)

    chart = alt.Chart(agg_df).mark_line(
        point=alt.OverlayMarkDef(filled=True, fill='white', size=60, strokeWidth=2),
        strokeWidth=3,
        interpolate='monotone'
    ).encode(
        x=alt.X('Year:T', title='', axis=alt.Axis(
            grid=False, labelColor='#64748b', domainColor='#e2e8f0', tickColor='#e2e8f0'
        )),
        y=alt.Y(f'{y_col}:Q', title='', axis=alt.Axis(
            grid=True, gridColor='#f1f5f9', gridDash=[4, 4],
            labelColor='#64748b', domain=False, ticks=False,
            labelExpr=vega_label_expr_for_metric(y_col)
        )),
        color=alt.value(color),
        # The standardized values ​​were also used in the chart tooltip.
        tooltip=[
            alt.Tooltip('Year:T', title='Year'),
            alt.Tooltip('FormattedValue:N', title='Value')
        ]
    ).properties(width='container', height=height).configure_view(strokeOpacity=0)

    return chart.to_html()

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

    options = get_select_options_for_group(selected_group)
    label = label_map.get(selected_group, "Selection")
    value = options[0]['value'] if options else None
    return label, options, value

@app.callback(
    [Output('year-start-label', 'children'),
     Output('year-start-label', 'style'),
     Output('year-end-label', 'children'),
     Output('year-end-label', 'style')],
    [Input('year-slider', 'drag_value'),
     Input('year-slider', 'value')]
)
def update_year_labels(drag_range, value_range):
    year_range = drag_range if drag_range is not None else value_range
    if not year_range or len(year_range) != 2:
        return "", {"left": "0%"}, "", {"left": "100%"}

    start_year, end_year = year_range
    start_style = slider_label_style(start_year, YEAR_MIN, YEAR_MAX, side="left")
    end_style = slider_label_style(end_year, YEAR_MIN, YEAR_MAX, side="right")
    return str(start_year), start_style, str(end_year), end_style

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
    # If no data is found, a blank page will be returned.
    if filtered.empty:
        return (
            env_html, econ_html, sdg_html,
            blank, blank, blank, blank, blank, blank,
            blank, blank, blank, blank, blank, blank, blank
        )

    years = sorted(filtered['Year'].dropna().unique())
    # If the year is less than two years, return blank.
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

    def calc_kpi(col):
        if col not in filtered.columns:
            return blank, blank
        # KPI calls the corresponding formatter
        formatter = get_metric_formatter(col)
        curr = c_df[col].mean(skipna=True)
        prev = p_df[col].mean(skipna=True)
        # This section describes how KPIs handle missing values.
        if pd.isna(curr):
            return blank, blank
        # KPI calls the corresponding formatter
        curr_display = formatter(curr)
        # If data from the previous year is missing, the current value is retained, and comparison is left blank.
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

    co2_v, co2_s = calc_kpi('CO2_Emissions')
    gdp_v, gdp_s = calc_kpi('GDP')
    natres_v, natres_s = calc_kpi('Nat_Res_Depletion')
    inf_v, inf_s = calc_kpi('Inflation')
    wom_v, wom_s = calc_kpi('Women_Parliament')
    hlt_v, hlt_s = calc_kpi('Life_Exp')

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
        hlt_v, hlt_s,
        regime
    )

if __name__ == '__main__':
    app.run(debug=True, port=8050)