from application import app
from flask import render_template, redirect, url_for, request
from application.form import UserInputForm

from application import vis

@app.route('/')
def index():
    return render_template('index.html', title='INDEX')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    form = UserInputForm()

    if request.method == "POST":
        category = form.category.data
        target = form.feature.data
    else:
        category = 'MO'
        target = 'Temperature'

    # category = request.args.get('category', default='MO')
    # target = request.args.get('target', default='Temperature')

    script0, div0 = vis.distribution_plot(target)
    script1, div1 = vis.boxplot_chart(category, target)
    script2, div2 = vis.avg_per_category_barplot(category, target)
    script3, div3 = vis.avg_quarter_year_barplot(target)
    script4, div4 = vis.line_circle_plot_top_10(target, 10)
    script = [script0] + [script1] + [script2] + [script3] + [script4]
    div = [div0] + [div1] + [div2] + [div3] + [div4]

    return render_template(
        'dashboard.html',
        form=form,
        script=script,
        div=div,
        cdn_css=vis.cdn_css,
        cdn_js=vis.cdn_js,
        title='DASHBOARD'
    )


@app.route('/gan')
def gan():
    return render_template('gan.html', title='INDEX')