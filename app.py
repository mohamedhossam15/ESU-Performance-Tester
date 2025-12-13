import os
import uuid
from flask import Flask,render_template,request,redirect,session
import psycopg2
import psycopg2.extras
from datetime import datetime
from pyexpat.errors import messages

app = Flask(__name__)

app.secret_key = "mekrek"

database_session = psycopg2.connect(user="neondb_owner", password="q1MunQWs8NlG", host="ep-tiny-fog-a5upxz0d.us-east-2.aws.neon.tech", port="5432",dbname="neondb")


@app.route('/register', methods=['GET', 'POST'])
def register():
    message=request.args.get('msg')
    if request.method == 'GET':
        return render_template("register.html", msg=message)
    if request.method == 'POST':
        radio=request.form.get('radio')
        firstname=request.form.get('firstname')
        lastname=request.form.get('lastname')
        username=request.form.get('username')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        blood_group = request.form.get('blood_group')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        birth = request.form.get('birth')
        profile_pic=request.files.get('profile_pic')
        print(radio)
        if profile_pic and profile_pic.filename:
            pic_name = str(uuid.uuid1()) + os.path.splitext(profile_pic.filename)[1]
            save_path = os.path.join('static/images/', pic_name)
            profile_pic.save(save_path)
            print(f"File saved to: {save_path}")
        else:
            message="No file uploaded or invalid file"
            print(message)
            return redirect(f"/register?msg={message}")
        if birth:
            date_birth = datetime.strptime(birth, '%Y-%m-%d')
            year = date_birth.year
        if firstname=="" or lastname=="" or username=="" or password=="" or confirm_password=="" or blood_group=="" or phone=="" or birth=="" or gender=="":
            message="There is an empty field"
        elif blood_group not in ["A", "A+", "A-", "AB+", "AB-", "B+", "B-", "O+", "O-"]:
            message="Re-entre the Blood Group"
        elif password != confirm_password:
            message="Passwords don't match"
        elif len(password) <= 6:
            message = "Passwords is too short"
        elif len(str(phone)) != 11:
            message = "incorrect phone number"
        elif gender not in ["Male", "male", "female", "Female", "MALE", "FEMALE"]:
            message = "Please enter a valid gender"
        elif "@gmail.com" not in username:
            message = "Please enter a valid username"
        elif year > 2024:
            message = "Please enter a valid birth"
        else:
            cur_patient=database_session.cursor()
            cur_doctor=database_session.cursor()
            cur_nurse=database_session.cursor()
            cur_admin=database_session.cursor()
            cur_patient.execute("SELECT username from Patient where username=%s",(username,))
            cur_doctor.execute("SELECT username from Doctor where username=%s",(username,))
            cur_nurse.execute("SELECT username from Nurse where username=%s",(username,))
            cur_admin.execute("SELECT username from Admin where username=%s",(username,))

            if cur_patient.fetchone() or cur_doctor.fetchone() or cur_nurse.fetchone() or cur_admin.fetchone():
                message="Username already exists"
            else:
                if cur_patient.fetchone() is None and radio =="Patient" :
                    cur_patient.execute(
                        "INSERT INTO Patient(firstname, lastname, username, password, blood_group, phone, gender, birth, type, pic_name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (firstname, lastname, username, password, blood_group, phone, gender, birth, radio, pic_name))
                elif cur_doctor.fetchone() is None and radio =="Doctor" :
                    cur_patient.execute(
                    "INSERT INTO Doctor(firstname, lastname, username, password, blood_group, phone, gender, birth, type, pic_name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (firstname, lastname, username, password, blood_group, phone, gender, birth, radio, pic_name))
                elif cur_nurse.fetchone() is None and radio == "Nurse":
                    cur_nurse.execute(
                        "INSERT INTO Nurse(firstname, lastname, username, password, blood_group, phone, gender, birth, type, pic_name) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (firstname, lastname, username, password, blood_group, phone, gender, birth, radio, pic_name))
                else:
                    message="Type of user doesn't exist"
                    return redirect(f"/register?msg={message}")
                database_session.commit()
                message="Username created successfully"
        return redirect(f"/register?msg={message}")

@app.route('/login',methods=['GET', 'POST'])
def login():
    message=request.args.get('msg')
    if request.method == 'GET':
        return render_template("login.html",msg=message)
    elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            cur_patient=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur_patient.execute("SELECT * from Patient where username=%s and password=%s",(username,password))
            userdata_patient = cur_patient.fetchone()
            cur_doctor=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur_doctor.execute("SELECT * from Doctor where username=%s and password=%s",(username,password))
            userdata_doctor = cur_doctor.fetchone()
            cur_nurse=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur_nurse.execute("SELECT * from Nurse where username=%s and password=%s",(username,password))
            userdata_nurse = cur_nurse.fetchone()
            cur_admin=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur_admin.execute("SELECT * from Admin where username=%s and password=%s",(username,password))
            userdata_admin = cur_admin.fetchone()
            if userdata_patient:
                    print(dict(userdata_patient),"patient")
                    session['user'] = dict(userdata_patient)
                    return redirect(f"/profile")
            elif userdata_doctor:
                    print(dict(userdata_doctor),"doctor")
                    session['user'] = dict(userdata_doctor)
                    return redirect(f"/profile")
            elif userdata_nurse:
                print(dict(userdata_nurse), "nurse")
                session['user'] = dict(userdata_nurse)
                return redirect(f"/profile")
            elif userdata_admin:
                print(dict(userdata_admin), "nurse")
                session['user'] = dict(userdata_admin)
                return redirect(f"/profile")
            else:
                    message = "username or password is incorrect"
                    return redirect(f"/login?msg={message}")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user', None)
    return redirect("/login")

@app.route('/profile', methods=['GET', 'POST'])
def profile():  # put application's code here
    userdata=session.get('user')
    message=request.args.get('msg')
    return render_template("profile.html",userdata=userdata,msg=message)

@app.route('/', methods=['GET', 'POST'])
def home():  # put application's code here
    userdata=session.get('user')
    return render_template("index.html", userdata=userdata)

@app.route('/about', methods=['GET', 'POST'])
def about():  # put application's code here
    userdata=session.get('user')
    return render_template("about.html", userdata=userdata)

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():  # put application's code here
    userdata=session.get('user')
    if userdata["type"] == "Patient":
        cur_appointment = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_appointment.execute(
            "SELECT * from Appointment a1 ,Doctor d1 where d1.id = a1.doctor_id and a1.patient_id = %s",
            (userdata["id"],))
        appointment_data = cur_appointment.fetchall()
        cur_doctor = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_doctor.execute("SELECT firstname, lastname, id from Doctor ")
        userdata_doctor = cur_doctor.fetchall()
        if request.method == 'GET':
            print(appointment_data)
            return render_template("patientAppointment.html", userdata=userdata, userdata_doctor=userdata_doctor, appointment_data=appointment_data)
        if request.method == 'POST':
            selected_id = request.form.get('selected_id')
            date = request.form.get('date')
            time = request.form.get('time')
            cur_doctor.execute("INSERT INTO VirtualAppointment(patient_id, doctor_id, date, time) values(%s,%s,%s,%s)",
                        (userdata["id"], selected_id, date, time))
            database_session.commit()
            return redirect("/appointment")
    elif userdata["type"] == "Doctor":
        cur_doctor = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_doctor.execute("SELECT * from VirtualAppointment a1 ,Patient p1 where p1.id = a1.patient_id and a1.doctor_id = %s",(userdata["id"],))
        userdata_doctor = cur_doctor.fetchall()
        cur_appointment = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_appointment.execute("SELECT * from Appointment a1 ,Patient p1 where p1.id = a1.patient_id and a1.doctor_id = %s",(userdata["id"],))
        appointment_data = cur_appointment.fetchall()
        return render_template("doctorAppointment.html", userdata=userdata, userdata_doctor=userdata_doctor, appointment_data=appointment_data)
    return redirect("/")
@app.route('/service', methods=['GET', 'POST'])
def service():  # put application's code here
    userdata=session.get('user')
    return render_template("service.html", userdata=userdata)

@app.route('/delete/<username>/<typ>', methods=['GET', 'POST'])
def delete(username,typ):  # put application's code here
    if typ == "Patient":
        cur_patient = database_session.cursor()
        cur_patient.execute("DELETE from Patient where username=%s", (username,))
    elif typ == "Doctor":
        cur_doctor = database_session.cursor()
        cur_doctor.execute("DELETE from Doctor where username=%s", (username,))
    else:
        cur_nurse = database_session.cursor()
        cur_nurse.execute("DELETE from Nurse where username=%s", (username,))
    database_session.commit()
    return redirect("/admin")

@app.route('/accept/<int:patient_id>/<int:doctor_id>/<date>/<time>', methods=['GET', 'POST'])
def accept(patient_id,doctor_id,date,time):  # put application's code here
    cur_patient_appointment = database_session.cursor()
    cur_patient_appointment.execute("INSERT INTO Appointment(patient_id, doctor_id, date, time) values(%s,%s,%s,%s)",
                            (patient_id,doctor_id,date,time))
    cur_patient_delete = database_session.cursor()
    cur_patient_delete.execute("DELETE from VirtualAppointment where patient_id=%s and doctor_id=%s and date=%s and time=%s", (patient_id,doctor_id,date,time))
    database_session.commit()
    return redirect("/appointment")

@app.route('/deleteappointment/<int:patient_id>/<int:doctor_id>/<date>/<time>', methods=['GET', 'POST'])
def deleteappointment(patient_id,doctor_id,date,time):  # put application's code here
    cur_patient = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur_patient.execute("DELETE from VirtualAppointment where patient_id=%s and doctor_id=%s and date=%s and time=%s", (patient_id,doctor_id,date,time))
    database_session.commit()
    return redirect("/appointment")

@app.route('/admin', methods=['GET', 'POST'])
def admin():  # put application's code here
    userdata=session.get('user')
    cur_admin = database_session.cursor()
    cur_admin.execute("SELECT username from Admin")
    user_admin=cur_admin.fetchone()
    if  user_admin and userdata["username"] in user_admin:
        cur_patient=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_patient.execute("SELECT * from Patient")
        user_p=cur_patient.fetchall()
        cur_doctor=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_doctor.execute("SELECT * from Doctor")
        user_d=cur_doctor.fetchall()
        cur_nurse=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_nurse.execute("SELECT * from Nurse")
        user_n=cur_nurse.fetchall()
        all_users = user_p + user_d + user_n
        number_patient=len(user_p)
        number_doctor=len(user_d)
        number_nurse=len(user_n)
        cur_patient_blood=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_patient_blood.execute("SELECT blood_group, count(id) from Patient group by blood_group")
        user_p_blood=cur_patient_blood.fetchall()
        cur_patient_gender=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_patient_gender.execute("SELECT gender, count(id) from Patient group by gender")
        user_p_gender=cur_patient_gender.fetchall()
        cur_doctor_blood=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_doctor_blood.execute("SELECT blood_group, count(id) from Doctor group by blood_group")
        user_d_blood=cur_doctor_blood.fetchall()
        cur_doctor_gender=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_doctor_gender.execute("SELECT gender, count(id) from Doctor group by gender")
        user_d_gender=cur_doctor_gender.fetchall()
        cur_nurse_blood=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_nurse_blood.execute("SELECT blood_group, count(id) from Nurse group by blood_group")
        user_n_blood=cur_nurse_blood.fetchall()
        cur_nurse_gender=database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_nurse_gender.execute("SELECT gender, count(id) from Nurse group by gender")
        user_n_gender=cur_nurse_gender.fetchall()
        return render_template("admin.html", all_users=all_users, user_p_blood=user_p_blood, user_d_blood=user_d_blood, user_n_blood=user_n_blood, user_p_gender=user_p_gender, user_d_gender=user_d_gender, user_n_gender=user_n_gender, number_patient=number_patient, number_doctor=number_doctor, number_nurse=number_nurse,userdata=userdata)
    elif userdata:
        return redirect(f"/profile")
    else:
        return redirect("/login")

@app.route('/edit', methods=['GET', 'POST'])
def edit():  # put application's code here
    # return render_template("edit.html", userdata=userdata)
    message=request.args.get('msg')
    userdata = session.get('user')
    if request.method == 'GET':
        return render_template("edit.html",userdata=userdata,msg=message)
    if request.method == 'POST':
        person_id=request.form.get('person_id')
        # firstname=userdata['firstname']
        # lastname=userdata['lastname']
        # password=userdata['password']
        blood_group=request.form.get('blood_group')
        username=request.form.get('username')
        phone=request.form.get('phone')
        gender=request.form.get('gender')
        birth=request.form.get('birth')
        typer=request.form.get('typer')
        profile_pic=request.files.get('profile_pic')
        scan_pic=request.files.get('scan_pic')
        if profile_pic and profile_pic.filename:
            pic_name = str(uuid.uuid1()) + os.path.splitext(profile_pic.filename)[1]
            save_path = os.path.join('static/images/', pic_name)
            profile_pic.save(save_path)
            print(f"File saved to: {save_path}")
        else:
            message="No file uploaded or invalid file"
            pic_name = None
            print(message)
            # return render_template("edit.html", msg=message, userdata=userdata)
        if scan_pic and scan_pic.filename:
            scan_name = str(uuid.uuid1()) + os.path.splitext(scan_pic.filename)[1]
            save_scan_path = os.path.join('static/scans/', scan_name)
            scan_pic.save(save_scan_path)
            print(f"File saved to: {save_scan_path}")
        else:
            message = "No file uploaded or invalid file"
            scan_name = None
            print(message)
        date_birth = datetime.strptime(birth, '%Y-%m-%d')
        year = date_birth.year
        cur_patient=database_session.cursor()
        cur_patient.execute("SELECT * from Patient where id=%s",(person_id,))
        cur_doctor=database_session.cursor()
        cur_doctor.execute("SELECT * from Doctor where id=%s",(person_id,))
        cur_nurse=database_session.cursor()
        cur_nurse.execute("SELECT * from Nurse where id=%s",(person_id,))
        cur_admin = database_session.cursor()
        cur_admin.execute("SELECT * from Admin where id=%s", (person_id,))
        cur_patient_user = database_session.cursor()
        cur_doctor_user = database_session.cursor()
        cur_nurse_user = database_session.cursor()
        cur_admin_user = database_session.cursor()
        cur_patient_user.execute("SELECT username from Patient where username=%s", (username,))
        cur_doctor_user.execute("SELECT username from Doctor where username=%s", (username,))
        cur_nurse_user.execute("SELECT username from Nurse where username=%s", (username,))
        cur_admin_user.execute("SELECT username from Admin where username=%s", (username,))
        if username=="" or blood_group=="" or phone=="" or birth=="" or gender=="":
            message="There is an empty field"
            return redirect(f"/edit?msg={message}")
        elif blood_group not in ["A", "A+", "A-", "AB+", "AB-", "B+", "B-", "O+", "O-"]:
            message="Re-entre the Blood Group"
            return redirect(f"/edit?msg={message}")
        elif len(str(phone)) != 10:
            message = "incorrect phone number"
            return redirect(f"/edit?msg={message}")
        elif gender not in ["Male", "male", "female", "Female", "MALE", "FEMALE"]:
            message = "Please enter a valid gender"
            return redirect(f"/edit?msg={message}")
        elif "@gmail.com" not in username:
            message = "Please enter a valid username"
            return redirect(f"/edit?msg={message}")
        elif year > 2024 :
            message = "Please enter a valid birth"
            return redirect(f"/edit?msg={message}")
        else:
            print(typer)
            if cur_patient.fetchone() and (typer=="Patient" or typer=="patient"):
                print("in")
                cur_user_insert = database_session.cursor()
                if pic_name is None and scan_name is None:
                    cur_user_insert.execute(
                        "UPDATE Patient SET phone = %s, gender = %s, birth = %s, blood_group = %s  WHERE id = %s",
                        (phone, gender, birth, blood_group, person_id))
                    database_session.commit()
                elif scan_name:
                    cur_user_insert.execute(
                        "UPDATE Patient SET phone = %s, gender = %s, birth = %s, blood_group = %s, scan_name = %s  WHERE id = %s",
                        (phone, gender, birth, blood_group, scan_name, person_id))
                    database_session.commit()
                else:
                    cur_user_insert.execute("UPDATE Patient SET phone = %s, gender = %s, birth = %s, blood_group = %s, pic_name = %s  WHERE id = %s",(phone,gender,birth,blood_group,pic_name,person_id))
                    database_session.commit()
                cur_user_check = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur_user_check.execute("SELECT * from Patient where id=%s", (person_id,))
                cur_user=cur_user_check.fetchone()
                print(dict(cur_user))
                session['user'] = dict(cur_user)
                if cur_patient_user.fetchone() or cur_doctor_user.fetchone() or cur_nurse_user.fetchone() or cur_admin_user.fetchone():
                    message = "All data updated successfully except username is already exist"
                    return redirect(f"/profile?msg={message}")
                else:
                    cur_user_insert.execute(
                        "UPDATE Patient SET username = %s  WHERE id = %s",
                        (username, person_id))
                    database_session.commit()
                    cur_user_check.execute("SELECT * from Patient where id=%s", (person_id,))
                    cur_user = cur_user_check.fetchone()
                    print(dict(cur_user))
                    session['user'] = dict(cur_user)
                return redirect(f"/profile")
            elif cur_doctor.fetchone() and (typer=="Doctor" or typer=="doctor"):
                cur_user_insert = database_session.cursor()
                if pic_name is None:
                    cur_user_insert.execute(
                        "UPDATE Doctor SET phone = %s, gender = %s, birth = %s, blood_group = %s WHERE id = %s",
                        (phone, gender, birth, blood_group, person_id))
                    database_session.commit()
                else:
                    cur_user_insert.execute("UPDATE Doctor SET phone = %s, gender = %s, birth = %s, blood_group = %s, pic_name = %s WHERE id = %s",(phone,gender,birth,blood_group,pic_name,person_id))
                    database_session.commit()
                cur_user_check = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur_user_check.execute("SELECT * from Doctor where id=%s", (person_id,))
                cur_user=cur_user_check.fetchone()
                session['user'] = dict(cur_user)
                if cur_patient_user.fetchone() or cur_doctor_user.fetchone() or cur_nurse_user.fetchone() or cur_admin_user.fetchone():
                    message = "All data updated successfully except username is already exist"
                    return redirect(f"/profile?msg={message}")
                else:
                    cur_user_insert.execute(
                        "UPDATE Doctor SET username = %s  WHERE id = %s",
                        (username, person_id))
                    database_session.commit()
                    cur_user_check.execute("SELECT * from Dcotor where id=%s", (person_id,))
                    cur_user = cur_user_check.fetchone()
                    print(dict(cur_user))
                    session['user'] = dict(cur_user)
                return redirect(f"/profile")
            elif cur_nurse.fetchone() and (typer == "Nurse" or typer == "nurse"):
                cur_user_insert = database_session.cursor()
                if pic_name is None:
                    cur_user_insert.execute(
                        "UPDATE Nurse SET phone = %s, gender = %s, birth = %s, blood_group = %s WHERE id = %s",
                        (phone, gender, birth, blood_group, person_id))
                    database_session.commit()
                else:
                    cur_user_insert.execute(
                        "UPDATE Nurse SET phone = %s, gender = %s, birth = %s, blood_group = %s, pic_name = %s WHERE id = %s",
                        (phone, gender, birth, blood_group, pic_name, person_id))
                    database_session.commit()
                cur_user_check = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur_user_check.execute("SELECT * from Nurse where id=%s", (person_id,))
                cur_user = cur_user_check.fetchone()
                session['user'] = dict(cur_user)
                if cur_patient_user.fetchone() or cur_doctor_user.fetchone() or cur_nurse_user.fetchone() or cur_admin_user.fetchone():
                    message = "All data updated successfully except username is already exist"
                    return redirect(f"/profile?msg={message}")
                else:
                    cur_user_insert.execute(
                        "UPDATE Nurse SET username = %s  WHERE id = %s",
                        (username, person_id))
                    database_session.commit()
                    cur_user_check.execute("SELECT * from Nurse where id=%s", (person_id,))
                    cur_user = cur_user_check.fetchone()
                    print(dict(cur_user))
                    session['user'] = dict(cur_user)
                return redirect(f"/profile")
            elif cur_admin.fetchone() and (typer == "Nurse" or typer == "nurse"):
                cur_user_insert = database_session.cursor()
                if pic_name is None:
                    cur_user_insert.execute(
                        "UPDATE Admin SET phone = %s, gender = %s, birth = %s, blood_group = %s WHERE id = %s",
                        (phone, gender, birth, blood_group, person_id))
                    database_session.commit()
                else:
                    cur_user_insert.execute(
                        "UPDATE Admin SET phone = %s, gender = %s, birth = %s, blood_group = %s, pic_name = %s WHERE id = %s",
                        (phone, gender, birth, blood_group, pic_name, person_id))
                    database_session.commit()
                cur_user_check = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur_user_check.execute("SELECT * from Admin where id=%s", (person_id,))
                cur_user = cur_user_check.fetchone()
                session['user'] = dict(cur_user)
                if cur_patient_user.fetchone() or cur_doctor_user.fetchone() or cur_nurse_user.fetchone() or cur_admin_user.fetchone():
                    message = "All data updated successfully except username is already exist"
                    return redirect(f"/profile?msg={message}")
                else:
                    cur_user_insert.execute(
                        "UPDATE Admin SET username = %s  WHERE id = %s",
                        (username, person_id))
                    database_session.commit()
                    cur_user_check.execute("SELECT * from Admin where id=%s", (person_id,))
                    cur_user = cur_user_check.fetchone()
                    print(dict(cur_user))
                    session['user'] = dict(cur_user)
                return redirect(f"/profile")
            else:
                print("out")
                message = "Error, There is no such user or Type of the user is incorrect"
                return render_template("edit.html",msg=message,userdata=userdata)



@app.route('/editadmin/<username>/<typ>', methods=['GET', 'POST'])
def editadmin(username,typ):
    if typ == "Patient":
        cur_user_get = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_user_get.execute("SELECT * from Patient where username=%s", (username,))
    elif typ == "Doctor":
        cur_user_get = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_user_get.execute("SELECT * from Doctor where username=%s", (username,))
    else:
        cur_user_get = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur_user_get.execute("SELECT * from Nurse where username=%s", (username,))
    cur_user = cur_user_get.fetchone()
    session['user1'] = dict(cur_user)
    cur_patient = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur_patient.execute("SELECT * from Patient")
    user_p = cur_patient.fetchall()
    cur_doctor = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur_doctor.execute("SELECT * from Doctor")
    user_d = cur_doctor.fetchall()
    cur_nurse = database_session.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur_nurse.execute("SELECT * from Nurse")
    user_n = cur_nurse.fetchall()
    all_users = user_p + user_d + user_n
    if request.method == 'GET':
        return render_template("editadmin.html", all_users=all_users, cur_user=cur_user)
    if request.method == 'POST':
        person_id = request.form.get('person_id')
        blood_group = request.form.get('blood_group')
        username = request.form.get('username')
        phone = request.form.get('phone')
        gender = request.form.get('gender')
        birth = request.form.get('birth')
        typer = request.form.get('typer')
        profile_pic = request.files.get('profile_pic')
        scan_pic = request.files.get('scan_pic')
        if profile_pic and profile_pic.filename:
            pic_name = str(uuid.uuid1()) + os.path.splitext(profile_pic.filename)[1]
            save_path = os.path.join('static/images/', pic_name)
            profile_pic.save(save_path)
            print(f"File saved to: {save_path}")
        else:
            message = "No file uploaded or invalid file"
            pic_name = None
            print(message)
            # return render_template("edit.html", msg=message, userdata=userdata)
        if scan_pic and scan_pic.filename:
            scan_name = str(uuid.uuid1()) + os.path.splitext(scan_pic.filename)[1]
            save_scan_path = os.path.join('static/scans/', scan_name)
            scan_pic.save(save_scan_path)
            print(f"File saved to: {save_scan_path}")
        else:
            message = "No file uploaded or invalid file"
            scan_name = None
            print(message)
        date_birth = datetime.strptime(birth, '%Y-%m-%d')
        year = date_birth.year
        cur_patient = database_session.cursor()
        cur_patient.execute("SELECT * from Patient where id=%s", (person_id,))
        cur_doctor = database_session.cursor()
        cur_doctor.execute("SELECT * from Doctor where id=%s", (person_id,))
        cur_nurse = database_session.cursor()
        cur_nurse.execute("SELECT * from Nurse where id=%s", (person_id,))
        if username == "" or blood_group == "" or phone == "" or birth == "" or gender == "":
            message = "There is an empty field"
            return redirect(f"/editadmin/{cur_user['username']}/{cur_user['type']}?msg={message}")
        elif blood_group not in ["A", "A+", "A-", "AB+", "AB-", "B+", "B-", "O+", "O-"]:
            message = "Re-entre the Blood Group"
            return redirect(f"/editadmin/{cur_user['username']}/{cur_user['type']}?msg={message}")
        elif len(str(phone)) != 10:
            message = "incorrect phone number"
            return redirect(f"/editadmin/{cur_user['username']}/{cur_user['type']}?msg={message}")
        elif gender not in ["Male", "male", "female", "Female", "MALE", "FEMALE"]:
            message = "Please enter a valid gender"
            return redirect(f"/editadmin/{cur_user['username']}/{cur_user['type']}?msg={message}")
        elif "@gmail.com" not in username:
            message = "Please enter a valid username"
            return redirect(f"/editadmin/{cur_user['username']}/{cur_user['type']}?msg={message}")
        elif year > 2024:
            message = "Please enter a valid birth"
            return redirect(f"/editadmin/{cur_user['username']}/{cur_user['type']}?msg={message}")
        else:
            if cur_patient.fetchone() and (typer == "Patient" or typer == "patient"):
                cur_user_insert = database_session.cursor()
                if pic_name is None and scan_name is None:
                    cur_user_insert.execute(
                        "UPDATE Patient SET phone = %s, gender = %s, birth = %s, username = %s, blood_group = %s  WHERE id = %s",
                        (phone, gender, birth, username, blood_group, person_id))
                    database_session.commit()
                elif scan_name:
                    cur_user_insert.execute(
                        "UPDATE Patient SET phone = %s, gender = %s, birth = %s, username = %s, blood_group = %s, scan_name = %s  WHERE id = %s",
                        (phone, gender, birth, username, blood_group, scan_name, person_id))
                    database_session.commit()
                else:
                    cur_user_insert.execute(
                        "UPDATE Patient SET phone = %s, gender = %s, birth = %s, username = %s, blood_group = %s, pic_name = %s  WHERE id = %s",
                        (phone, gender, birth, username, blood_group, pic_name, person_id))
                    database_session.commit()
            elif cur_doctor.fetchone() and (typer == "Doctor" or typer == "doctor"):
                cur_user_insert = database_session.cursor()
                if pic_name is None:
                    cur_user_insert.execute(
                        "UPDATE Doctor SET phone = %s, gender = %s, birth = %s, username = %s, blood_group = %s WHERE id = %s",
                        (phone, gender, birth, username, blood_group, person_id))
                    database_session.commit()
                else:
                    cur_user_insert.execute(
                        "UPDATE Doctor SET phone = %s, gender = %s, birth = %s, username = %s, blood_group = %s, pic_name = %s WHERE id = %s",
                        (phone, gender, birth, username, blood_group, pic_name, person_id))
                    database_session.commit()
            elif cur_nurse.fetchone() and (typer == "Nurse" or typer == "nurse"):
                cur_user_insert = database_session.cursor()
                if pic_name is None:
                    cur_user_insert.execute(
                        "UPDATE Nurse SET phone = %s, gender = %s, birth = %s, username = %s, blood_group = %s WHERE id = %s",
                        (phone, gender, birth, username, blood_group, person_id))
                    database_session.commit()
                else:
                    cur_user_insert.execute(
                        "UPDATE Nurse SET phone = %s, gender = %s, birth = %s, username = %s, blood_group = %s, pic_name = %s WHERE id = %s",
                        (phone, gender, birth, username, blood_group, pic_name, person_id))
                    database_session.commit()
            return redirect("/admin")

if __name__ == '__main__':
    app.run()

