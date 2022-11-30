import numpy as np
import pandas as pd

from scipy.stats.kde import gaussian_kde

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
from bokeh.layouts import row
from bokeh.layouts import column


from flask import send_file

# Nhúng css và js của bokeh
cdn_css = CDN.css_files
cdn_js = CDN.js_files[0]


# Load dataset
df = pd.read_csv('data/5years.csv')

# Add date
df['DATE'] = df['MO'].astype('string') + '-' + df['DY'].astype('string') + '-' + df['YEAR'].astype('string')
df['DATE'] = pd.to_datetime(df['DATE'], format='%m-%d-%Y')

# Features
FEATURES = [
    "Temperature", "Relative_Humidity", "Specific_Humidity",
    "Precipitation", "Pressure", "Wind_Speed", "Wind_Direction"
]

# Strategies
STRATEGIES = [
    "gan", "knn", "random",
]

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
    Chart thể hiện: Lấy statistics về dataset HTML table dạng
    Input:
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def df_original():
    return df.to_html(classes='table table-striped caption-top table-hover')

"""
    Chart thể hiện: Lấy statistics về dataset HTML table dạng
    Input:
    Output:
        * html: code html
"""
def df_statistics():
    return df[FEATURES].describe().to_html(classes='table table-striped caption-top table-hover')


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
            tooltips=[
                ('Tháng: ', '@ranges'),
                ('Mức độ ' + col + ' trung bình: ', '@counts{0.02f}')
            ],
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
        pd.DataFrame({
            'DATE': [df.loc[i]['DATE'] for i in idx_top],
            'COL': [df.loc[i][col] for i in idx_top]
        })
    )
    source_line = ColumnDataSource(pd.DataFrame({
        'DATE': df['DATE'],
        'COL': df[col]
    }))

    # Figure
    p = figure(
        x_axis_type='datetime',
        height=700,
        width=1500,
        tools='save, pan, box_zoom, wheel_zoom, reset',
    )

    # Plot
    p.line(x='DATE', y='COL', source=source_line, line_color='#747C92', line_width=1)
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
            tooltips=[
                ('Ngày: ', '@DATE{%F}'),
                ('Mức độ ' + col + ': ', '@COL')
            ],
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
            tooltips=[
                ('Năm / Quý: ', '@x'),
                ('Mức độ ' + col + ' trung bình: ', '@counts')
            ],
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

"""
    Chart thể hiện: Distribution của từng biến
    Input:
        * col: Chọn feature
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def distribution_plot(col):
    hist, edges = np.histogram(df[col], density=True, bins=50)

    p = figure(
        height=750,
        width=750,
        x_axis_label=col, 
        y_axis_label='Mật độ (Density)',
        title='Phân phối của thuộc tính ' + col,
        toolbar_location='below',
        tools='save, pan, box_zoom, wheel_zoom, reset'
    )

    p.quad(
        bottom=0, top=hist, left=edges[:-1], right=edges[1:],
        line_color="white", fill_color='red', fill_alpha=0.75,
        hover_fill_alpha=1.0, hover_fill_color='navy'
    )

    from scipy.stats.kde import gaussian_kde
    pdf = gaussian_kde(df[col])
    x = np.linspace(df[col].min(), df[col].max(), 1000)
    p.line(
        x='top', y='right',
        source=ColumnDataSource(
            pd.DataFrame({
                'top': x,
                'right': pdf(x)
            })
        ),
        line_width=5
    )

    # Add tools
    p.add_tools(
        HoverTool(
            tooltips=[
                ('Mật độ (Density): ', '@top'),
                ('Mức độ ' + col + ': ', '@right')
            ],
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
    
    script, div = components(p)

    return script, div

"""
    Chart thể hiện: Boxplot của từng biến theo category
    Input:
        * col: Chọn feature
        * category: Chọn biến phân loại
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def boxplot_chart(category, col):

    data = df[[category, col]]
    x_range = [str(x) for x in df[category].unique()]

    # find the quartiles and IQR for each category
    groups = data.groupby(category)
    q1 = groups.quantile(q=0.25)
    q2 = groups.quantile(q=0.5)
    q3 = groups.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    lower = q1 - 1.5 * iqr

    # find the outliers for each category
    def outliers(group):
        cat = group.name
        return group[
            (group[col] > upper.loc[cat][col]) |
            (group[col] < lower.loc[cat][col])
        ][col]
    out = groups.apply(outliers).dropna()

    # prepare outlier data for plotting, we need coordinates for every outlier.
    if not out.empty:
        outx = list(out.index.get_level_values(0))
        outy = list(out.values)

    p = figure(
        x_range=x_range,
        height=750,
        width=750,
        x_axis_label=category, 
        y_axis_label=col,
        title='Boxplot của thuộc tính ' + col + ' theo ' + category,
        toolbar_location='below',
        tools='save, pan, box_zoom, wheel_zoom, reset'
    )

    # if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
    qmin = groups.quantile(q=0.00)
    qmax = groups.quantile(q=1.00)
    upper[col] = [min([x,y]) for (x,y) in zip(list(qmax.loc[:,col]),upper[col])]
    lower[col] = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,col]),lower[col])]

    # stems
    p.segment(x_range, upper[col], x_range, q3[col], line_color="black")
    p.segment(x_range, lower[col], x_range, q1[col], line_color="black")

    # boxes
    p.vbar(x_range, 0.7, q2[col], q3[col], fill_color="#E08E79", line_color="black")
    p.vbar(x_range, 0.7, q1[col], q2[col], fill_color="#3B8686", line_color="black")

    # whiskers (almost-0 height rects simpler than segments)
    p.rect(x_range, lower[col], 0.2, 0.01, line_color="black")
    p.rect(x_range, upper[col], 0.2, 0.01, line_color="black")

    # outliers
    if not out.empty:
        source_circle = ColumnDataSource(
            pd.DataFrame(dict(
                x=list(np.array(outx) - 0.5),
                y=outy
            ))
        )
        p.circle(
            x='x',
            y='y',
            source=source_circle,
            size=6,
            color="#F38630",
            fill_alpha=0.6
        )

    # Add tools
    p.add_tools(
        HoverTool(
            tooltips=[
                (col, '@bottom'),
                (category, '@x')
            ],
            mode='mouse'
        )
    )

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="16px"
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    # Title
    p.title_location = "above"
    p.title.text_font_size = "25px"
    p.title.align = "center"
    p.title.background_fill_color = None
    p.title.text_color = "black"

    script, div = components(p)

    return script, div


def regression_plot(colx, coly):

    x = df[colx]
    y = df[coly]

    source_data = ColumnDataSource({'x': x, 'y': y})

    p = figure(
        height=505,
        width=505,
        x_axis_label=colx, 
        y_axis_label=coly,
        title='Regression Plot ' + colx + ' theo ' + coly,
        toolbar_location='below',
        tools='save, pan, box_zoom, wheel_zoom, reset'
    )

    p.circle(
        x='x',
        y='y',
        source=source_data,
        size=6,
        color='red'
    )

    # Line
    par = np.polyfit(x, y, 1, full=True)
    slope = par[0][0]
    intercept = par[0][1]
    y_predicted = [slope * i + intercept  for i in x]

    p.line(
        x, y_predicted,
        color='grey',
        line_width=4
    )

    # Add tools
    p.add_tools(
        HoverTool(
            tooltips=[
                (colx + ': ', '@x'),
                (coly + ' : ', '@y')
            ],
            mode='mouse'
        )
    )

    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    # Title
    p.title_location = "above"
    p.title.text_font_size = "15px"
    p.title.align = "center"
    p.title.background_fill_color = None
    p.title.text_color = "black"
    
    return p


"""
    Chart thể hiện: Regresion plot của feature với tất cả biến còn lại
    Input:
        * col: Chọn feature
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def regresion_plot_full(col):
    cols = [
        'Temperature', 'Relative_Humidity', 'Specific_Humidity',
        'Precipitation', 'Pressure', 'Wind_Speed', 'Wind_Direction'
    ]
    cols.remove(col)

    r = []
    for c in cols:
        r += [regression_plot(col, c)]
        
    script, div = components(column(row(r[:3]), row(r[3:])))

    return script, div

"""
    Chart thể hiện: Plot 1 thuộc tính / 1 phương pháp
    Input:
        * strategy: Phương pháp điền khuyết
        * col: Chọn feature
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def plot_pred_and_real(strategy, col, s=0, e=1826):

    # Get data
    mask = np.array(pd.read_csv('data_plot/mask.csv'))
    real = np.array(df[FEATURES])
    imputed = np.array(pd.read_csv('data_plot/' + strategy + '.csv'))
    
    # col => idx (0, 1, 2, 3, 4, 5, 6)
    cols = dict([(fea, idx) for fea, idx in zip(FEATURES, range(len(FEATURES)))])

    prediction = np.multiply(mask, imputed)[s:e].T[cols[col]]
    real_value = np.multiply(mask, real)[s:e].T[cols[col]]

    # Xóa hết giá trị 0
    # prediction = np.delete(prediction, np.where(prediction == 0))
    # real_value = np.delete(real_value, np.where(real_value == 0))

    x_range = [str(x) for x in list(range(s, e))]

    # y_min = np.min(np.array(np.min(prediction), np.min(real_value)))
    # y_max = np.max(np.array(np.max(prediction), np.max(real_value))) 
    # y_range = [str(y) for y in range(int(y_min), int(y_max) + 1)]

    source_prediction = ColumnDataSource({
        'x': x_range, 'y': prediction,
        'z': np.array(['Giá trị đự đoán'] * len(prediction))
    })
    source_real_value = ColumnDataSource({
        'x': x_range, 'y': real_value,
        'z': np.array(['Giá trị thực tế'] * len(real_value))
    })

    p = figure(
        height=505,
        width=505,
        #x_range=x_range,
        #y_range=y_range,
        x_axis_label='Vị trí của điểm dữ liệu', 
        y_axis_label=col,
        title='So sánh giữa dữ liệu điền khuyết và dữ liệu thực tế',
        toolbar_location='below',
        tools='save, pan, box_zoom, wheel_zoom, reset'
    )

    # Prediction
    p.circle(
        x='x',
        y='y',
        source=source_prediction,
        size=6,
        color='red',
        legend_label='Giá trị dự đoán'
    )

    # Real value
    p.circle(
        x='x',
        y='y',
        source=source_real_value,
        size=6,
        color='blue',
        legend_label='Giá trị thực tế'
    )
    
    # # Add tools
    p.add_tools(
        HoverTool(
            tooltips=[
                ('Điểm dữ liệu: ', '@x'),
                ('Giá trị ' + col + ' :', '@y'),
                ('Thuộc nhóm :', '@z')
            ],
            mode='mouse'
        )
    )

    p.xaxis.major_label_orientation = 1
    p.xgrid.grid_line_color = None

    # Title
    p.title_location = "above"
    p.title.text_font_size = "15px"
    p.title.align = "center"
    p.title.background_fill_color = None
    p.title.text_color = "black"

    # Legend
    p.legend.title = "Loại"
    
    return p

"""
    Chart thể hiện: Plot n thuộc tính / 1 phương pháp
    Input:
        * strategy: Phương pháp điền khuyết
        * col: Chọn feature
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def plot_pred_and_real_all(strategy, s=0, e=1826):
    cols = [
        'Temperature', 'Relative_Humidity', 'Specific_Humidity',
        'Precipitation', 'Pressure', 'Wind_Speed', 'Wind_Direction'
    ]

    plot = []
    for c in cols:
        plot += [plot_pred_and_real(strategy, c, s, e)]
        
    return plot

"""
    Chart thể hiện: Plot n thuộc tính / n phương pháp hoặc tất cả
    Input:
        * strategy: Phương pháp điền khuyết
    Output:
        * script: Đoạn script của chart
        * div: Đoạn div của chart
"""
def plot_red_and_real_all_strategy(strategy, s=0, e=1826):
    if strategy != 'All':
        plot = plot_pred_and_real_all(strategy, s, e)
        script, div = components(column(row(plot[:3]), row(plot[3:]), plot[-1]))
    else:
        plot = [column(plot_pred_and_real_all(st, s, e)) for st in STRATEGIES]
        plot = row(plot)
        script, div = components(plot)
    return script, div