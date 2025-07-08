import plotly.express as px
from shiny.express import input, ui, render
from shinywidgets import render_plotly
from shiny import reactive, req
import seaborn as sns
from palmerpenguins import load_penguins

penguins_df = load_penguins()
species_list: list = penguins_df["species"].unique().tolist()
island_list: list = penguins_df["island"].unique().tolist()

def format_name(name) -> str:
    split_name: list = name.rsplit("_", 1)
    new_name: str = split_name[0].replace("_", " ").title() + f" ({split_name[1]})"
    return new_name

penguins_df.columns = [
    format_name(name) if penguins_df.dtypes[name] == float else name.title()
    for name in penguins_df.columns
]
penguins_df["Sex"] = penguins_df["Sex"].str.title()
continuous_variables: list = penguins_df.select_dtypes(include=float).columns.tolist()

ui.tags.style(
    """
    .card-with-shadow {box-shadow: 0px 4px 8px rgba(0, 0, 75, 0.5);}
    #my_sidebar {box-shadow: 0px 4px 8px rgba(0, 0, 75, 0.5);}
    """
)
ui.page_opts(title="Penguin Data By Jordan", fillable=True)

with ui.sidebar(open="open", id="my_sidebar"):
    ui.h2("Sidebar")
    ui.input_selectize("selected_attribute", "Select Attribute", continuous_variables)
    ui.input_numeric("plotly_bin_count", "Plotly Histogram Bins", 50)
    ui.input_slider("seaborn_bin_count", "Seaborn Histogram Bins", 10, 344, 50)
    ui.input_checkbox_group(
        "selected_species_list",
        "Select Species",
        choices = species_list,
        selected = species_list,
        inline = True,
    )
    ui.input_checkbox_group(
        "selected_island_list",
        "Select Island",
        choices = island_list,
        selected = island_list,
        inline = True,
    )
    ui.input_selectize(
        "selected_attribute_y_scatter",
        "Scatterplot y-axis Attribute",
        continuous_variables[::-1],
    )
    ui.hr()
    ui.a("GitHub", href="https://github.com/JfromNWMS/cintel-02-data", target="_blank")


@reactive.calc
def filtered_data():
    req(input.selected_species_list(), input.selected_island_list())
    is_species_match = penguins_df["Species"].isin(input.selected_species_list())
    is_island_match = penguins_df["Island"].isin(input.selected_island_list())
    filtered_penguins_df = penguins_df[is_species_match & is_island_match]
    req(not filtered_penguins_df.empty)
    return filtered_penguins_df


with ui.layout_columns():

    with ui.card(full_screen=True, class_="card-with-shadow"):

        @render.data_frame
        def datatable():
            return render.DataTable(filtered_data(), height="185px")

    with ui.card(full_screen=True, class_="card-with-shadow"):

        @render.data_frame
        def datagrid():
            return render.DataGrid(filtered_data())


with ui.layout_columns():

    with ui.card(full_screen=True, class_="card-with-shadow"):
        ui.card_header("Plotly Histogram: Species")

        @render_plotly
        def plotly_hist():
            px_hist = px.histogram(
                data_frame = filtered_data(),
                x = input.selected_attribute(),
                nbins = input.plotly_bin_count(),
                color = "Species",
                template = "plotly_white",
                opacity = 0.5
            )
            px_hist.update_yaxes(
                title_text = px_hist.layout.yaxis.title.text.title(),
            )
            return px_hist

    with ui.card(full_screen=True, class_="card-with-shadow"):
        ui.card_header("Seaborn Histogram: Species")

        @render.plot
        def sns_hist():
            sns.set_style("whitegrid")
            sns.histplot(
                data = filtered_data(),
                x = input.selected_attribute(),
                bins = input.seaborn_bin_count(),
                hue = "Species",
            )


with ui.card(full_screen=True, class_="card-with-shadow"):
    ui.card_header("Plotly Scatterplot: Species")

    @render_plotly
    def plotly_scatterplot():
        px_scatter = px.scatter(
            data_frame = filtered_data(),
            x = input.selected_attribute(),
            y = input.selected_attribute_y_scatter(),
            color = "Species",
            opacity = 0.7,
            symbol = "Sex",
            hover_data = "Island",
            template = "plotly_white",
        )
        return px_scatter
