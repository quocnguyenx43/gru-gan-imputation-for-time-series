import numpy as np
import pandas as pd

from bokeh.plotting import figure, show, output_notebook, output_file
from bokeh.palettes import all_palettes
from bokeh.models import (
    HoverTool, LabelSet, Legend, ColumnDataSource,
    LinearColorMapper, BasicTicker, PrintfTickFormatter,
    ColorBar, GeoJSONDataSource, FactorRange
)
from bokeh.models.transforms import LinearInterpolator
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.io import curdoc


from flask import send_file

# Nhúng css và js của bokeh
cdn_css = CDN.css_files
cdn_js = CDN.js_files[0]


# Load dataset
df = pd.read_csv('data/final.csv')

# Add date
df['DATE'] = df['MO'].astype('string') + '-' + df['DY'].astype('string') + '-' + df['YEAR'].astype('string')
df['DATE'] = pd.to_datetime(df['DATE'], format='%m-%d-%Y')

# Add Quarter
def mo_to_qua(mo):
    if mo <= 3:
        return 1
    elif mo > 3 and mo <= 6:
        return 2
    elif mo > 6 and mo <= 9:
        return 3
    else:
        return 4

df['QUARTER'] = df['MO'].map(mo_to_qua)


"""
    Chart thể hiện: AVG của biến theo năm hoặc tháng
    Input:
        * category: YEAR hoặc MO
        * col: Các features còn lại
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def avg_per_category_barplot(category, col):
    df_temp = df[[category, col]]
    df_groupby = df_temp.groupby([category], as_index=False).mean()

    # Sources
    ranges = [str(x) for x in list(df_groupby[category])]
    counts = [str(x) for x in list(df_groupby[col])]
    source = ColumnDataSource(data=dict(ranges=ranges, counts=counts))

    # Theme
    curdoc().theme = "dark_minimal"

    # Figure
    p = figure(
        y_range=ranges,
        width=500,
        height=400,
        x_axis_label=col,
        y_axis_label=category,
        title="Trung bình " + col + " theo " + category,
        toolbar_location="below",
        tools='save, pan, box_zoom, wheel_zoom, reset'
    )
    p.hbar(y='ranges', right='counts', source=source, height=0.8)

    # Add tools    
    p.add_tools(
        HoverTool(
            tooltips="Năm: @ranges <br> Mức độ " + col + " trung bình: @counts",
            #formatters={'@ranges': 'int'},
            mode='mouse'
        )
    )

    # Title
    p.title_location = "above"
    p.title.text_font_size = "25px"
    p.title.align = "center"
    p.title.background_fill_color = None
    p.title.text_color = "black"
    
    # Return
    script, div = components(p)
    return script, div

"""
    Chart thể hiện: Lineplot của các features theo thời gian và chọn ra n ngày cao nhất
    Input:
        * col: Chọn feature
        * n: Số ngày cao nhất nhất
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def line_circle_plot_top_10(col, n):
    # Get indeces
    idx_top = df.sort_values(by=col, ascending=False)[:n].index

    # Sources
    source_circle = ColumnDataSource(
        pd.DataFrame(dict(
            DATE=[df.loc[i]['DATE'] for i in idx_top],
            COL=[df.loc[i][col] for i in idx_top]
        ))
    )
    source_line = ColumnDataSource(df)

    # Figure
    p = figure(
        x_axis_type='datetime',
        plot_height=700,
        plot_width=1500,
        tools='save, pan, box_zoom, wheel_zoom, reset',
    )

    # Plot
    p.line(x='DATE', y=col, source=source_line, line_color='#747C92', line_width=1)
    p.circle(
        x='DATE', 
        y='COL', 
        source=source_circle,
        #size=15
        size={
            'field': 'COL',
            'transform': LinearInterpolator(
                    x=[df[col].min(), df[col].max()],
                    y=[1, 30]
            )
        },
        color='#3A2449'
    )

    p.add_tools(
        HoverTool(
            tooltips="<b>Ngày: </b> @DATE{%F} <br> <b>Mức độ " + col + ": </b> @" + col,
            formatters={'@DATE': 'datetime'},
            mode='mouse'
        )
    )

    # Title
    p.title_location = "above"
    p.title.text_font_size = "25px"
    p.title.align = "center"
    p.title.background_fill_color = None
    p.title.text_color = "black"

    p.xaxis.axis_label = 'Ngày'
    p.yaxis.axis_label = col
    p.title.text = "Biểu đồ đột biến của " + col + " và " + str(n) + " ngày có mức độ " + col + " cao nhất"

    script, div = components(p)

    return script, div

"""
    Chart thể hiện: AVG của biến theo từng quý trong các năm
    Input:
        * col: Chọn feature
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def avg_quarter_year_barplot(col):
    df_temp = df[['YEAR', 'QUARTER', col]]
    df_groupby = df_temp.groupby(['YEAR', 'QUARTER'], as_index=False).mean()

    curdoc().theme = "dark_minimal"

    # Source
    years = [str(x) for x in list(df_groupby['YEAR'].unique())]
    quarters = [str(x) for x in list(df_groupby['QUARTER'].unique())]

    data = {
        'YEAR': years,
        '1': list(df_groupby[df_groupby['QUARTER'] == 1][col]),
        '2': list(df_groupby[df_groupby['QUARTER'] == 2][col]),
        '3': list(df_groupby[df_groupby['QUARTER'] == 3][col]),
        '4': list(df_groupby[df_groupby['QUARTER'] == 4][col]),
    }

    x = [(year, quarter) for year in years for quarter in quarters]
    counts = sum(zip(data['1'], data['2'], data['3'], data['4']), ())

    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(
        x_range=FactorRange(*x),
        width=1000,
        height=400,
        x_axis_label='Quý trong năm',
        y_axis_label=col,
        title="Trung bình " + col + " theo Quý trong các Năm",
        toolbar_location="below",
        tools='save, pan, box_zoom, wheel_zoom, reset'
    )

    p.vbar(x='x', top='counts', width=0.8, source=source)

    # Add tools    
    p.add_tools(
        HoverTool(
            tooltips="Năm, Quý: @x<br>Mức độ " + col + ": @counts",
            mode='mouse'
        )
    )

    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    # Title
    p.title_location = "above"
    p.title.text_font_size = "25px"
    p.title.align = "center"
    p.title.background_fill_color = None
    p.title.text_color = "black"
    
    # Return
    script, div = components(p)
    return script, div