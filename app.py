from flask import Flask, render_template, url_for, request, flash, redirect, session
import os
from fileinput import filename
import sqlite3
import pandas as pd
from io import StringIO
from werkzeug.utils import secure_filename


# SELECT email,password,proxy,port, COUNT(*) AS CNT FROM Allyahooseeds GROUP BY email,password,proxy,port HAVING count(*) > 1;
# SELECT email,password,proxy,port, COUNT(*) FROM Allyahooseeds GROUP BY email,password,proxy,port;

app = Flask(__name__)
app.secret_key="123"

# USER LOGIN DATABASE TABLE
con = sqlite3.connect("database.db")
con.execute('''CREATE TABLE IF NOT EXISTS Logindetails
                    (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL)''')
con.close()

# CSV DATABASE TABLE
con1 = sqlite3.connect("database.db")
cur1 = con1.execute('''CREATE TABLE IF NOT EXISTS Allyahooseeds(
                    ID INTEGER PRIMARY KEY ASC AUTOINCREMENT,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    proxy TEXT NOT NULL,
                    port TEXT NOT NULL
                    )''')
con1.close()

# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}

# Upload folder
#UPLOAD_FOLDER = os.path.join("static", "files")
UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER



@app.route("/")
def home():
    return render_template('home.html')

@app.route("/Dashboard.html")
def dashboard():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    # cur.execute("INSERT INTO Logindetails(email, password) VALUES(?,?)",(username, password))
    sql3 = f"SELECT count(*) FROM Allyahooseeds"
    cur.execute(sql3)
    rowvalues = cur.fetchone()
    return render_template('Dashboard.html', rowvalues = rowvalues)

@app.route("/register.html", methods = ['GET', 'POST'])
def register():
    #return render_template("register.html")
    if request.method == "POST":
        try:
            username = request.form['email']
            password = request.form['password']

            con = sqlite3.connect("database.db")
            cur = con.cursor()
            # cur.execute("INSERT INTO Logindetails(email, password) VALUES(?,?)",(username, password))
            sql2 = f"INSERT INTO Logindetails(email,password) SELECT '{username}', '{password}' WHERE NOT EXISTS(SELECT * From Logindetails WHERE email='{username}')"
            cur.execute(sql2)
            con.commit()
            con.close()
            flash("Records Added Successfully","Success")
        except Exception as e:
            flash(f"Error In Insert Opertaion: {str(e)}", "Danger")
        finally:
            return redirect(url_for("login"))
            #return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login.html", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM Logindetails WHERE email=? and password=?", (email, password))
            
            user_login_data = cur.fetchone()

            if results:
                session["email"] = results["email"]
                session["password"] = results["password"]
                # flash("Records Added Successfully","Success")
                return render_template("Dashboard.html", user_login_data=user_login_data)
            else:
                error = "Invalid Username and Password"
                # flash("Username and password Mismatch", "danger")
        except Exception as e:
            flash(f"Error In SELECT * Opertaion: {str(e)}", "Danger")
        finally:
            # return redirect(url_for("login"))
            return render_template("Dashboard.html")
            con.close()

    return render_template("login.html")
           
@app.route('/sign_out')
def sign_out():
    session.clear()
    return redirect(url_for('login'))


@app.route("/csv_upload.html", methods=['GET', 'POST'])
def csv_upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            print(f"Uploaded File : {uploaded_file}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)
            # print(f"final: {file_path}")
            parseCSV(file_path)

            # connection = sqlite3.connect("database.db")
            # cur2 = connection.cursor()
            # cur2.execute("SELECT * FROM Allyahooseeds")
            # values = cur2.fetchall()
            # connection.close()

    return render_template('csv_upload.html')
            
    #return render_template('csv_upload.html')

    
def parseCSV(filepath):
    # print("inside parse")
    col_name = ['Email','Password','Proxy','Port']

    csvData = pd.read_csv(filepath)
    #print(csvData)

    for i, row in csvData.iterrows():        
        # print(row['Email'], row['Password'], row['Proxy'], row['Port'])
        e = row['Email']
        p = row['Password']
        p_ip = row['Proxy']
        p_prt = row['Port']
        # sql = f"INSERT INTO Allyahooseeds (email,password,proxy,port) VALUES ('{e}','{p}','{p_ip}','{p_prt}')" 
        sql = f"INSERT INTO Allyahooseeds (email,password,proxy,port) SELECT '{e}','{p}','{p_ip}','{p_prt}' WHERE NOT EXISTS (SELECT * FROM Allyahooseeds WHERE email='{e}')"
        
        conn1 = sqlite3.connect("database.db")
        cur = conn1.cursor()

        cur.execute(sql)
        conn1.commit()
        print(i, row['Email'], row['Password'], row['Proxy'], row['Port'])
    

    #return render_template('csv_upload.html')


@app.route("/show_csv_data.html", methods= ['GET', 'POST'])
def show_csv():
    rowvalues = None
    # if request.method == 'POST':
    print("Display DATA")
    conn_disp = sqlite3.connect("database.db")

    cur_disp = conn_disp.cursor()

    cur_disp.execute("SELECT * FROM Allyahooseeds")

    rowvalues = cur_disp.fetchall()

    # conn_disp.close()
    
    #return rowvalues

    return render_template("show_csv_data.html", rowvalues=rowvalues)



if __name__ == "__main__":
    app.run(debug = True, port=5000)