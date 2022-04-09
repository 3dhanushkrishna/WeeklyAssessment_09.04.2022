from flask import Flask, request, render_template, session
import sqlite3

from flask_session import Session
from werkzeug.utils import redirect
from datetime import date

data = sqlite3.connect("Report.db",check_same_thread=False)
table1 = data.execute("select * from sqlite_master where type = 'table' and name = 'Crime'").fetchall()
table2 = data.execute("select * from sqlite_master where type = 'table' and name = 'User'").fetchall()

if table1!=[]:
    print("Crime table already exists")
else:
    data.execute('''create table Crime(
                            ID INTEGER primary key autoincrement,
                            Description TEXT,
                            Remarks TEXT,
                            Date TEXT);''')
    print("Table created")
if table2!=[]:
    print("User table already exists")
else:
    data.execute('''create table User(
                            ID INTEGER primary key autoincrement,
                            Name TEXT,
                            Address TEXT,
                            Email TEXT,
                            Phone INTEGER,
                            Password TEXT);''')
    print("User Table created")

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/',methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        getUsername = request.form["name"]
        getPassword = request.form["pass"]
        print(getUsername)
        print(getPassword)
        if getUsername == "admin" and getPassword == "12345":
            return redirect('/dashboard')
        else:
            return redirect('/')
    return render_template("adminlogin.html")

@app.route('/dashboard')
def admin_dashboard():
    return render_template("admindashboard.html")

@app.route('/viewall')
def viewall_report():
    cursor = data.cursor()
    count = cursor.execute("select * from Crime")

    result = cursor.fetchall()
    return render_template("viewall.html",crime=result)


@app.route('/sortdate',methods=['GET','POST'])
def search_date():
    if request.method == 'POST':
        getDate = str(request.form["date"])
        cursor = data.cursor()
        count = cursor.execute("select * from Crime where date='"+getDate+"' ")
        result = cursor.fetchall()
        if result is None:
            print("There is no CrimeReports on",getDate)
        else:
            return render_template("sortdate.html",crime=result,status=True)
    else:
        return render_template("sortdate.html",crime=[],status=False)




@app.route('/register',methods=['GET','POST'])
def User_register():
    if request.method == 'POST':
        getName = request.form["username"]
        getAddress = request.form["address"]
        getEmail = request.form["useremail"]
        getPhone = request.form["userphone"]
        getPass = request.form["userpass"]
        print(getName,getAddress,getEmail,getPhone)
        try:
            data.execute("insert into user(name,address,email,phone,password) \
            values('"+getName+"','"+getAddress+"','"+getEmail+"',"+getPhone+",'"+getPass+"')")
            data.commit()
            print("Inserted Successfully")
            return redirect('/complaint')
        except Exception as err:
            print(err)
    return render_template("register.html")

@app.route('/user',methods=['GET','POST'])
def Login_user():
    if request.method == 'POST':
        getEmail = request.form["useremail"]
        getPass = request.form["userpass"]
        cursor = data.cursor()
        query = "select * from user where email='"+getEmail+"' and password='"+getPass+"' "
        result = cursor.execute(query).fetchall()
        if len(result)>0:
            for i in result:
                getName = i[1]
                getId = i[0]
                session["name"] = getName
                session["id"] = getId
                if (getEmail == i[3] and getPass == i[5]):
                    print("password correct")
                    return redirect('/usersession')

                else:
                    return render_template("userlogin.html",status=True)
    else:
        return render_template("userlogin.html",status=False)

@app.route('/userdashboard')
def user_dashboard():
    return render_template("userdashboard.html")

@app.route('/usersession')
def userpage():
    if not session.get("name"):
        return redirect('/')
    else:
        return render_template("usersession.html")


@app.route('/complaint',methods=['GET','POST'])
def report_crime():
    if request.method == 'POST':
        getDescription = request.form["description"]
        getRemark = request.form["remark"]
        print(getDescription)
        print(getRemark)
        getDate = str(date.today())
        cursor = data.cursor()
        query = "insert into Crime(description,remarks,date) values('"+getDescription+"','"+getRemark+"','"+getDate+"')"
        cursor.execute(query)
        data.commit()
        print(query)
        print("Inserted Successfully")
        return redirect('/user')
    return render_template("complaint_reports.html")

@app.route('/update',methods=['GET','POST'])
def user_update():
    try:
        if request.method == 'POST':
            getname = request.form["newname"]
            print(getname)
            cursor = data.cursor()
            count = cursor.execute("select * from User where name='" + getname + "' ")
            result = cursor.fetchall()
            print(len(result))
            return render_template("edituser.html",searchname=result)
        return render_template("edituser.html")
    except Exception as err:
        print(err)


@app.route('/edit',methods=['GET','POST'])
def User_edit():
    if request.method == 'POST':
        getName = request.form["newname"]
        getAddress = request.form["newaddress"]
        getEmail = request.form["newemail"]
        getPhone = request.form["newphone"]
        getPass = request.form["newpass"]
        try:
            query = "update user set address='" + getAddress + "',email='" + getEmail + "',phone=" + getPhone + ",password='" + getPass + "' where name='" + getName + "'"
            print(query)
            data.execute(query)
            data.commit()
            print("Edited Successfully")
            return redirect('/viewall')
        except Exception as error:
            print(error)

    return render_template("edituser.html")

@app.route('/logout')
def logout():
    session["name"] = None
    return redirect('/')



if __name__=="__main__":
    app.run()