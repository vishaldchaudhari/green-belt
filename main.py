from flask import Flask, render_template, request, redirect, session
import mysql.connector
from mysql.connector import cursor
import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import webbrowser

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = mysql.connector.connect(
    host='csscdb.c8vuupkpr2gy.ap-southeast-2.rds.amazonaws.com',
    user='admin',
    password='Vishal18',
    database='CSSC'
)

cursor = conn.cursor()


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/register')
def about():
    return render_template('register.html')


@app.route('/home')
def home():
    if 'id' in session:
        return render_template('home.html')
    else:
        return redirect('/')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['id'] = users[0][0]
        return redirect('/home')
    else:
        return redirect('/')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin_validation', methods=['POST'])
def admin_validation():
    key = request.form.get('key')
    password = request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `key` LIKE '{}' AND `password` LIKE '{}'""".format(key, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['id'] = users[0][0]
        return redirect('/dmaic')
    else:
        return redirect('/admin')


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('username')
    mobile = request.form.get('usermobile')
    email = request.form.get('useremail')
    password = request.form.get('userpassword')

    cursor.execute("""INSERT INTO `users` (`id`,`name`,`mobile`,`email`,`password`) VALUES 
    (NULL,'{}','{}','{}','{}')""".format(name, mobile, email, password))
    conn.commit()

    return "User Registered Successfully"

@app.route('/data')
def data():
    return render_template('info.html')


@app.route('/add_data', methods=['POST'])
def add_data():
    duname = request.form.get('data_name')
    date = request.form.get('date')
    late = request.form.get('late')
    traffic = request.form.get('traffic')
    dproficiency = request.form.get('proficiency')
    doverall = request.form.get('overall')

    cursor.execute("""INSERT INTO `fill` (`did`,`dname`,`date`,`late`,`traffic`,`proficiency_d`,`overall`) VALUES 
        (NULL,'{}','{}','{}','{}','{}','{}')""".format(duname, date, late, traffic, dproficiency, doverall))
    conn.commit()
    return "Data added successfully."



def chi_square_test():
    # connect to the MySQL database
    cnx = mysql.connector.connect(
    host = 'csscdb.c8vuupkpr2gy.ap-southeast-2.rds.amazonaws.com',
    user ='admin',
    password = 'Vishal18',
    database = 'CSSC'
)

    cursor = cnx.cursor()

    # execute the query to get the data from the database
    query = ('SELECT late, traffic, proficiency_d FROM fill WHERE overall=1')
    cursor.execute(query)
    data = cursor.fetchall()

    # create a pandas DataFrame from the data
    df = pd.DataFrame(data, columns=['Late', 'Traffic', 'Proficiency'])

    # count the number of occurrences of each value in each column
    observed_values = df.apply(pd.value_counts).fillna(0)

    # calculate the expected values assuming a uniform distribution
    n = observed_values.sum().sum()
    expected_values = pd.DataFrame(np.ones(observed_values.shape) * n / observed_values.size, index=observed_values.index, columns=observed_values.columns)

    # calculate the chi-square statistic and p-value
    chi2, p, dof, expected = stats.chi2_contingency(observed_values)

    # plot the joint bar graph
    fig, ax = plt.subplots()
    index = np.arange(len(df.columns))
    bar_width = 0.35
    opacity = 0.8

    observed_bars = ax.bar(index, observed_values.mean(), bar_width,
                           alpha=opacity, color='b', label='Observed')
    expected_bars = ax.bar(index + bar_width, expected_values.mean(), bar_width,
                           alpha=opacity, color='g', label='Expected')

    ax.set_xlabel('Variable')
    ax.set_ylabel('Frequency')
    ax.set_title('Observed vs Expected')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(df.columns)
    ax.legend()

    graph_filename = 'static/observed_vs_expected.png'
    plt.savefig(graph_filename)

    # close the database connection
    cursor.close()
    cnx.close()
    plt.close()

    # return the results and graph filename
    result = f'Chi-square statistic: {chi2}, p-value: {p}, degrees of freedom: {dof}'
    return result, graph_filename

@app.route('/chisquare')
def index():
    result, graph_filename = chi_square_test()
    return render_template('chisquare.html', result=result, graph_filename=graph_filename)

@app.route('/ishikawa')
def ishikawa():
    return render_template('ishikawa.html')

@app.route('/fmea')
def fmea():
    return render_template('FMEA.html')

@app.route('/olr')
def olr():
    return render_template('OLR.html')

@app.route('/pc')
def pc():
    return render_template('PC.html')

@app.route('/hlpm')
def hlpm():
    return render_template('HLPM.html')

@app.route('/dps')
def dps():
    return render_template('dps.html')

@app.route('/dmaic')
def dmaic():
    return render_template('dmaic.html')



if __name__ == "__main__":
    app.run(debug=True)
