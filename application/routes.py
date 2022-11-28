from application import app
from flask import render_template, redirect, url_for, request
from application.form import UserInputForm

from application import vis

@app.route('/')
def index():
    return render_template('index.html', title='INDEX')

@app.route('/dashboard')
def dashboard():
    category = request.args.get('category', default='MO')
    target = request.args.get('target', default='Temperature')

    script1, div1 = vis.avg_per_category_barplot(category, target)
    script2, div2 = vis.line_circle_plot_top_10(target, 10)
    script3, div3 = vis.avg_quarter_year_barplot(target)

    script = [script1] + [script2] + [script3]
    div = [div1] + [div2] + [div3]

    return render_template(
        'dashboard.html', 
        script=script,
        div=div,
        cdn_css=vis.cdn_css,
        cdn_js=vis.cdn_js,
        title='DASHBOARD'
    )

@app.route('/change', methods=['GET', 'POST'])
def change():
    form = UserInputForm()
    if request.method == "POST":
        category_feature = form.category.data
        target_feature = form.feature.data
        return redirect(url_for('dashboard', category=category_feature, target=target_feature))
    else:
        return render_template('change.html', title='CHANGE', form=form)