import pymongo
from flask import Flask, render_template, request, redirect, url_for, flash
from bson.objectid import ObjectId
import re
from datetime import datetime
import os 
from dotenv import load_dotenv

app_path = os.path.join(os.path.dirname(__file__),'.')
dotenv_path = os.path.join(app_path,'.env')
load_dotenv(dotenv_path)


app = Flask('contactmanager')
app.secret_key = os.environ.get('SECRETKEY')

client = pymongo.MongoClient(os.environ.get('MONGOSTRING'))
db = client.contactmanager
contacts_collection = db.contacts
def is_valid_email(email):
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@app.route('/')
def index():

    all_contacts = list(contacts_collection.find())
    return render_template('index.html', contacts=all_contacts)

@app.route('/add', methods=['POST'])
def add_contact():

    if request.method == 'POST':
        full_name = request.form['fullName'].strip()
        phone_number = request.form['phoneNumber'].strip()
        email = request.form['email'].strip().lower()
        profilepicture = request.form['profilepicture'].strip()
        checkuser = contacts_collection.find_one({'phone':phone_number})

        if checkuser is not None:
            flash('Contact already exists with this phone number!','danger')
            return redirect('/')
        


        # 2. Check if name is empty or too short
        if not full_name:
            flash('Name must not be empty and must be at least 3 characters long.', 'danger')
            return redirect('/')

        # 3. Check if phone number is numeric
        if not phone_number.isdigit():
            flash('Phone number must contain only digits.', 'danger')
            return redirect('/')
            
        # 4. Check if email is provided
        if not email:
            flash('Email is a mandatory field.', 'danger')
            return redirect('/')
        emailValidationCheck = is_valid_email(email)
        if not emailValidationCheck:
            flash('Email format invalid','danger')
            return redirect('/')
        # --- Add to database if all validations pass ---
        new_contact = {
            'name': full_name,
            'phone': phone_number,
            'email': email,
            'timestamp':datetime.utcnow()
        }
        contacts_collection.insert_one(new_contact)
        flash('Contact added successfully!', 'success')
        
    return redirect('/')

@app.route('/delete')
def delete_contact():
    contactid = request.args['contactid']
    contacts_collection.delete_one({'_id': ObjectId(contactid)})
    flash('Contact deleted successfully!', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
