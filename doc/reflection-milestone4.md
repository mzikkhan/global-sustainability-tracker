# Milestone 4 Reflection for the Global Sustainability Tracker

## What we have in our prototype

Since Milestone 2 (our `app_v1.py` prototype), we have made significant architectural and feature enhancements to arrive at our final production-ready dashboard (`app.py`).

The core improvements and finalized functionalities are:

**1. Architectural Shift to Plotly & Multi-Page Layout**
- **Plotly Integration:** We migrated from rendering Altair charts inside HTML iframes (as seen in `app_v1.py`) to native Plotly Express (`dcc.Graph`) charts. This drastically improved chart interactivity, hover response times, and styling consistency.

**2. Enhanced Visualizations & Interactivity**
- **Dynamic Bubble Chart:** We implemented an animated bubble chart to explore the correlation between GDP, Life Expectancy, and CO2 Emissions over time. Users can customize the Y-axis metric and click on individual bubbles to instantly cross-filter the rest of the dashboard (KPIs and line charts) to that specific entity.
- **Comparison Redesign:** The new "Multi-Country Comparison" page allows users to directly compare two specific countries across any available KPI metric on a single, unified line chart.

**3. Advanced UI/UX Refinements**
- **Country Flags:** We integrated logic to parse ISO codes and inject Unicode national flags directly into the dropdown selectors for a premium feel.
- **Dynamic KPI Formatting:** KPI cards now intelligently format large numbers (K/M/B/T) and conditionally color percent changes based on whether an increase is culturally "good" (e.g., GDP) or "bad" (e.g., CO2 Emissions).

## What is not implemented (and why)

As part of scoping our final deliverable, the following features were considered but ultimately excluded from our production build for the reasons outlined below.

**1. Accessibility Enhancements (e.g., High Contrast Mode)**
We were suggested to add a toggleable high-contrast theme for visually impaired users. However, Dash components handle basic screen-reader compatibility under the hood, and implementing a robust custom dark/high-contrast mode required extensive conflicting CSS overrides. 

**2. Data Exports (CSV/PDF Downloads)**
A feature to let users download the currently filtered dataset or save the dashboard state as a PDF was suggested. We excluded this because Plotly's native toolbar already provides an "Export as PNG" option for individual charts, satisfying the core need for saving visual insights. 

**3. Page Loading Optimization (Data Subsetting / Caching)**
The guidelines suggested subsetting data to make the app snappier if it felt sluggish. While compiling `app.py`, we found that pandas `df_filtered` operations combined with native Plotly rendering handled the 18-year dataset efficiently on modern browsers. 

## Thoughts on Feedback Received from Peer/TA

**1. Ease of Use**
Both peers and TA found the dashboard easy to use, with clear instructions and intuitive navigation. They appreciated
the clear layout and separation of sections.

**2. Data Limitations**
One key feedback from our peers was that the data is outdated (2000-2018). We recognize the need to use more recent data for our economic and social factor analysis and will be looking to find more recent data sources for future improvements.

**3. Future Improvements**
We believe this can be a powerful tool for policy makers and environmental analysts, we hope to continue to improve it in the future by optimizing performance, improving accessibility, and updating the data.