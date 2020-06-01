from flask import render_template, request, Response, session # redirect, url_for,
from app import app
from app.forms import Form

import io
import numpy as np
from scipy.stats import beta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

@app.route('/', methods=['GET', 'POST'])
def home():

    form = Form()
    results = False

    # if no errors get data from form
    if form.validate_on_submit():

        num_reviews_A = form.num_reviews_A.data
        rating_A = form.rating_A.data
        num_reviews_B = form.num_reviews_B.data
        rating_B = form.rating_B.data

        ### calculate comparisons

        # number of succesful trials
        k_A = round(num_reviews_A*rating_A/100)
        k_B = round(num_reviews_B*rating_B/100)

        # expected rating
        expected_rating_A = (k_A + 1)/(num_reviews_A + 2)
        expected_rating_B = (k_B + 1)/(num_reviews_B + 2)
        #convert to % and round to 2 dp
        expected_rating_A = round(expected_rating_A*100, 2)
        expected_rating_B = round(expected_rating_B*100, 2)

        # scan of possible p ratings
        dp = 0.000001  # need fine enough grain.
        p_scan = np.arange(0,1+dp,dp)

        # pdf and cdf
        pdf_A = beta.pdf(p_scan, k_A + 1, num_reviews_A - k_A + 1)
        cdf_B = beta.cdf(p_scan, k_B + 1,num_reviews_B - k_B + 1)

        prob_AgtB = np.trapz(cdf_B*pdf_A, dx=dp)
        #convert to % and round to 2 dp
        prob_AgtB = round(prob_AgtB*100, 2)

        results = [expected_rating_A, expected_rating_B, prob_AgtB]

        session['beta_params'] = [num_reviews_A, k_A, num_reviews_B, k_B]

    return render_template('index.html', form=form, results=results)


@app.route('/plot_prob_densities.png')
def plot_png():
    """
    Renders the plot on the fly.
    """
    # calculating
    num_reviews_A, k_A, num_reviews_B, k_B = session.get('beta_params')

    p_scan = np.linspace(0,1,201)
    pdf_A = beta.pdf(p_scan, k_A + 1, num_reviews_A - k_A + 1)
    pdf_B = beta.pdf(p_scan, k_B + 1, num_reviews_B - k_B + 1)

    expected_rating_A = (k_A + 1)/(num_reviews_A + 2)
    expected_rating_B = (k_B + 1)/(num_reviews_B + 2)

    beta_max = max([max(pdf_A), max(pdf_B)])

    # plotting
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1, position=(0.1, 0.2, 0.8, 0.7))

    axis.plot(p_scan*100, pdf_A, label='A', c='b')
    axis.plot(p_scan*100, pdf_B, label='B', c='r')
    axis.vlines(expected_rating_A*100, 0, beta_max, colors='b', linestyles='--')
    axis.vlines(expected_rating_B*100, 0, beta_max, colors='r', linestyles='--')
    axis.set_xlabel('Actual Rating (%)')
    axis.set_ylabel('Relative Probability')
    axis.set_title('Relative Probabilities of Possible Actual Rating')
    axis.legend(loc='best')
    fig.text(.5, .05, "Dashed lines indicate expected actual rating", ha='center')

    output = io.BytesIO()
    FigureCanvasAgg(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")
