import plotly.express as px
from shiny.express import input, ui, render
from shinywidgets import render_plotly
from shiny import reactive
import seaborn as sns
from palmerpenguins import load_penguins

continuous_variables = load_penguins().select_dtypes(include=float).columns.to_list()

ui.page_opts(title="Penguin Data By Jordan", fillable=True)

with ui.sidebar(open="open"):
    ui.h2("Sidebar")
    ui.input_selectize(
        "selected_attribute",
        "Select Attribute",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    )
    ui.input_numeric("plotly_bin_count", "Plotly Histogram Bins", 50)
    ui.input_slider("seaborn_bin_count", "Seaborn Histogram Bins", 10, 344, 50)
    ui.input_checkbox_group(
        "selected_species_list",
        "Select Species",
        choices=["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=True,
    )
    ui.input_selectize(
        "selected_attribute_y_scatter",
        "Scatterplot y-axis Attribute",
        continuous_variables[::-1]
    )
    ui.hr()
    ui.a("GitHub", href="https://github.com/JfromNWMS/cintel-02-data", target="_blank")

@reactive.calc 
def penguins_df():
    species_list = input.selected_species_list()
    return load_penguins().query("species in @species_list")
    # Boolean indexing is most likely faster than .query() in this instance due to
    # low complexity of conditions and the dataset being of small-medium size

ui.tags.style(
        """
        .card-with-shadow {box-shadow: 0px 4px 8px rgba(0, 0, 100, 0.5);}
        """
)

with ui.layout_columns():

    with ui.card(full_screen=True, class_="card-with-shadow"):
        @render.data_frame
        def datatable():
            return render.DataTable(penguins_df(), height='185px')
            
    with ui.card(full_screen=True, class_="card-with-shadow"):
        @render.data_frame
        def datagrid():
            return render.DataGrid(penguins_df())

with ui.layout_columns():
    
    with ui.card(full_screen=True, class_="card-with-shadow"):
        @render_plotly
        def plotly_hist():
            px_hist = px.histogram(
                data_frame=penguins_df(),
                x=input.selected_attribute(),
                nbins=input.plotly_bin_count(),
                color='species'
            )
            return px_hist

    with ui.card(full_screen=True, class_="card-with-shadow"):
        @render.plot
        def sns_hist():
            sns.histplot(
                data = penguins_df(),
                x = input.selected_attribute(),
                bins = input.seaborn_bin_count(),
                hue = 'species'
            )

with ui.card(full_screen=True, class_="card-with-shadow"):

    ui.card_header("Plotly Scatterplot: Species")

    @render_plotly
    def plotly_scatterplot():
        px_scatter = px.scatter(
            data_frame = penguins_df(),
            x = input.selected_attribute(),
            y = input.selected_attribute_y_scatter(),
            color = 'species',
            symbol = 'sex',
            hover_data = 'island'
        )
        return px_scatter


    
