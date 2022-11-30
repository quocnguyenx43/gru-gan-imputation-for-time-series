from application import app
from flask import render_template, redirect, url_for, request
from application.form import ChangeInputFeatureForm, ChangeStrategyForm

from application import vis

@app.route('/')
def index():
    return render_template('index.html', title='INDEX')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    change_feature_form = ChangeInputFeatureForm()
    change_strategy_form = ChangeStrategyForm()

    if request.method == "POST":
        category = change_feature_form.category.data
        target = change_feature_form.feature.data
        strategy = change_strategy_form.strategy.data
    else:
        category = request.args.get('category', default='MO')
        target = request.args.get('target', default='Temperature')
        strategy = request.args.get('strategy', default='All')

    if category is None:
        category = 'MO'
    if target is None:
        target = 'Temperature'
    if strategy is None:
        strategy = 'All'

    df_statistics = vis.df_statistics()

    script0, div0 = vis.distribution_plot(target)
    script1, div1 = vis.boxplot_chart(category, target)
    script2, div2 = vis.avg_per_category_barplot(category, target)
    script3, div3 = vis.avg_quarter_year_barplot(target)
    script4, div4 = vis.line_circle_plot_top_10(target, 10)
    script5, div5 = vis.regresion_plot_full(target)

    # GAN
    script6, div6 = vis.plot_red_and_real_all_strategy(strategy)

    script = [script0] + [script1] + [script2] + [script3] + [script4] + [script5] + [script6]
    div = [div0] + [div1] + [div2] + [div3] + [div4] + [div5] + [div6]

    return render_template(
        'dashboard.html',
        change_feature_form=change_feature_form,
        change_strategy_form=change_strategy_form,
        strategy=strategy,
        script=script,
        df_statistics=df_statistics,
        div=div,
        cdn_css=vis.cdn_css,
        cdn_js=vis.cdn_js,
        title='DASHBOARD'
    )


@app.route('/gan', methods=['POST', 'GET'])
def gan():

    form = ChangeStrategyForm()

    if request.method == "POST":
        strategy = form.strategy.data
    else:
        strategy = 'GAN'

    script, div = vis.plot_pred_and_real_all('GAN')

    return render_template(
        'gan.html',
        form=form,
        script=script,
        div=div,
        cdn_css=vis.cdn_css,
        cdn_js=vis.cdn_js,
        title='GAN MODEL'
    )