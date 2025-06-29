from flask import Flask, render_template, request, redirect
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('adminlogin.html') 

@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    username = request.form['username']
    password = request.form['password']

    if username == 'aaiadmin' and password == 'aaiadmin123':
        return redirect('/adminpanel')
    else:
        return "Wrong username or password, Try again..."

@app.route('/adminpanel')
def admin_panel():
    return render_template('admindashboard.html')

@app.route('/import_xlsx', methods=['POST'])
def import_xlsx():
    data = []
    headers = []

    file = request.files['file']
    if file:
        df = pd.read_excel(file)  # Read XLSX
        headers = list(df.columns)
        data = df.values.tolist()

    return render_template('admindashboard.html', table_data=data, headers=headers)

if __name__ == '__main__':
    app.run(debug=True)




