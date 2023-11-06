from flask import Flask, render_template, request, redirect,send_file
import sqlite3, io
import pandas as pd



app = Flask(__name__)
DATABASE = 'test_database.db'
app.static_folder = 'static'

# Home Page
@app.route('/')
def home():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT date,bankname,summary from communication_log order by id desc limit 10')
    latest_communication_logs  = cursor.fetchall()
    cursor.execute('SELECT year,month,bankname from transaction_record order by id desc limit 15')
    latest_transaction_records   = cursor.fetchall()
    cursor.execute('SELECT name FROM sqlite_schema where type={}'.format("'table'"))
    tablename=cursor.fetchall()
    conn.close()
    return render_template('home.html',tablename=tablename,latest_communication_logs =latest_communication_logs, latest_transaction_records =latest_transaction_records)


@app.route('/add_bank', methods=['GET', 'POST'])
def add_bank():
    if request.method == 'POST':
        ID=request.form['bank_id']
        Init=request.form['Init']
        bankname = request.form['bank_name']
        cbs = request.form['cbs']
        team_formation = True if request.form.get('team_formation') else False
        progress = request.form['progress']
        expected_timeline = request.form['expected_timeline']
        BPM5_auto_or_manual = request.form['bpm5_auto_or_manual']
        itrs_on_inr = True if request.form.get('itrs_on_inr') else False

        # Save data to database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Bank VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", (ID,Init, bankname, cbs, team_formation, progress, expected_timeline, BPM5_auto_or_manual, itrs_on_inr))
        conn.commit()
        conn.close()
        return redirect('/add_bank')  # Redirect to the same page after submitting the form

    # Retrieve last two records from the Bank table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Bank')
    records = cursor.fetchall()
    conn.close()

    return render_template('add_bank.html', records=records)

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        dept = request.form['dept']
        is_primary = request.form.get('is_primary', False)
        bankname = request.form['bankname']

        # Insert the contact data into the Contacts table
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Contacts (Name, Email, Phone, Dept, is_primary, bankname) VALUES (?, ?, ?, ?, ?, ?)",(name, email, phone, dept, is_primary, bankname))
        conn.commit()
        conn.close()
        return redirect('/add_contact')  # Redirect to the same page after submitting the form

    # Retrieve last few records from the Contact table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts ORDER BY ID DESC')
    contact_data = cursor.fetchall()
    cursor.execute('SELECT init FROM Bank')
    banklist=cursor.fetchall()
    conn.close()

    return render_template('add_contact.html', contact_data=contact_data,banklist=banklist)

# Add Data Page - Meeting
@app.route('/add_meeting', methods=['GET', 'POST'])
def add_meeting():
    if request.method == 'POST':
        date = request.form['date']
        bankname = request.form['bankname']
        participants = request.form['participants']
        meeting_summary=request.form['meeting_summary']
        our_concern = request.form.get('our_concern', False)
        their_concern = request.form['their_concern']

        # Insert the contact data into the Contacts table
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Meeting (date, bankname, participant,meeting_summary, our_concern, their_concern) VALUES (?, ?, ?, ?, ?,?)",(date, bankname, participants,meeting_summary, our_concern, their_concern))
        conn.commit()
        conn.close()
        return redirect('/add_meeting')  # Redirect to the same page after submitting the form

    # Retrieve last two records from the Meeting table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Meeting ORDER BY date desc LIMIT 10;')
    meeting_data = cursor.fetchall()
    cursor.execute('SELECT init FROM Bank')
    banklist=cursor.fetchall()
    conn.close()

    return render_template('add_meeting.html', meeting_data=meeting_data,banklist=banklist)

# Add Data Page - Transaction Report
@app.route('/add_txn', methods=['GET', 'POST'])
def add_txn():
    if request.method == 'POST':
        bankname = request.form['bankname']
        year = request.form['year']
        month = request.form['month']
        nrb34 = bool(request.form.get('nrb34'))
        remarks_on_34 = request.form['remarks_on_34']
        response_on_34 = request.form['response_on_34']
        nrb46 = bool(request.form.get('nrb46'))
        remarks_on_46 = request.form['remarks_on_46']
        response_on_46 = request.form['response_on_46']

        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if the record exists
        query = "SELECT * FROM transaction_record WHERE bankname = ? AND year = ? AND month = ?"
        cursor.execute(query, (bankname, year, month))
        existing_record = cursor.fetchone()
        if existing_record:
            remarks_on_34=existing_record[5] +'\n'+remarks_on_34
            response_on_34=existing_record[6] +'\n'+response_on_34
            remarks_on_46=existing_record[8]+'\n'+remarks_on_46
            response_on_46=existing_record[9] +'\n'+response_on_46
            query = "UPDATE transaction_record SET remarks_on_34 = ?,response_on_34=?,nrb46=?,remarks_on_46=?,response_on_46=? WHERE bankname = ? AND year = ? AND month = ?"
            cursor.execute(query, (remarks_on_34,response_on_34,nrb46,remarks_on_46,response_on_46, bankname, year, month))
        else:
            cursor.execute("INSERT INTO transaction_record (bankname, year, month, NRB34, remarks_on_34, response_on_34, NRB46, remarks_on_46, response_on_46) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",(bankname, year, month, nrb34, remarks_on_34, response_on_34, nrb46, remarks_on_46, response_on_46))

    # Commit the changes and close the connection
        conn.commit()
        conn.close()
        return redirect('/add_txn')  # Redirect to the same page after submitting the form

    # Retrieve last two records from the Transaction Report table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT init FROM Bank')
    banklist=cursor.fetchall()
    conn.close()

    return render_template('add_txn.html', banklist=banklist)


@app.route('/communication_log', methods=['GET', 'POST'])
def communication_log():
    if request.method == 'POST':
        date = request.form['date']
        bankname = request.form['bankname']
        focal_person = bool(request.form.get('focal_person'))
        medium=request.form['medium']
        summary = request.form['summary']
        remarks = request.form['remarks']

        # Insert the contact data into the Contacts table
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO communication_log (date, bankname, focal_person,medium, summary, remarks) VALUES (?, ?, ?, ?, ?,?)",(date, bankname, focal_person,medium, summary, remarks))
        conn.commit()
        conn.close()
        return redirect('/communication_log')  # Redirect to the same page after submitting the form

    # Retrieve last few records from the Contact table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM communication_log ORDER BY ID DESC limit 10')
    log_data = cursor.fetchall()
    cursor.execute('SELECT init FROM Bank')
    banklist=cursor.fetchall()
    conn.close()
    return render_template('communication_log.html', log_data=log_data,banklist=banklist)


@app.route('/manage_special_remarks', methods=['GET', 'POST'])
def manage_special_remarks():
    if request.method == 'POST':
        bankname = request.form['bankname']
        s_remarks = request.form['s_remarks']

        # Insert the contact data into the Contacts table
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO special_remarks ( bankname, s_remarks) VALUES (?, ? )",(bankname, s_remarks))
        conn.commit()
        conn.close()
        return redirect('/manage_special_remarks')  # Redirect to the same page after submitting the form

    # Retrieve last two records from the Meeting table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM special_remarks ORDER BY ID desc LIMIT 20;')
    s_data = cursor.fetchall()
    cursor.execute('SELECT init FROM Bank')
    banklist=cursor.fetchall()
    conn.close()

    return render_template('manage_special_remarks.html', s_data=s_data,banklist=banklist)




@app.route('/report_generator', methods=['GET'])
def report_generator():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT Init FROM Bank')
    banklist = cursor.fetchall()
    conn.close()
    return render_template('report_generator.html', banklist=banklist)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    bankname = request.form['bankname']
    tables = request.form.getlist('tables[]')
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM Bank where init=(?)""",(bankname,))
    bankdata = cursor.fetchall()
    cursor.execute("SELECT * FROM transaction_record where bankname=(?)",(bankname,))
    transaction_record = cursor.fetchall()
    table_dict={}
    for t in tables:
        query = f"""SELECT * FROM {t} WHERE bankname = ? OR bankname LIKE ? OR bankname LIKE ? OR bankname LIKE ? OR bankname=?;"""
        data=cursor.execute(query, (bankname, f'{bankname},%', f'%, {bankname}', f'%, {bankname},%',bankdata[0][6])).fetchall()
        if len(data)>0:
            column_headers = [desc[0] for desc in cursor.description]
            Zdata=[] 
            for row in data:
                Zdata.append(dict(zip(column_headers, row)))
            table_dict[t]=Zdata
    conn.close()
    

    # Render the report template with the fetched data
    return render_template('report.html',bankdata=bankdata, transaction_record=transaction_record, table_dict=table_dict)

@app.route('/temp', methods=['GET'])
def temp():
    # conn = sqlite3.connect(DATABASE)
    # # cursor = conn.cursor()
    # df=pd.read_sql_query("select * from bank",conn)
    # conn.close()
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
        df = pd.read_excel(file)
        html_table = df.to_html(index=False)
        return send_file(io.BytesIO(html_table.encode()), attachment_filename='table.html', as_attachment=True)
    else:
        return 'Invalid file format. Please upload an Excel file.'
    

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        query = request.form['query']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(query)
        data=cursor.fetchall()
        column_headers = [desc[0] for desc in cursor.description]
        Zdata=[] 
        for row in data:
            Zdata.append(dict(zip(column_headers, row)))
        return render_template("query.html",table_data=Zdata)
    return render_template("query.html")




if __name__ == '__main__':
    app.run(debug=False)
