"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file contains the routes for your application.
"""

import os
from app import app, db ;
from flask import render_template, request, redirect, url_for, flash, session, send_from_directory
from app.models import Propertymod
from app.forms import PropertyForm
from werkzeug.utils import secure_filename


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Shauna Smith")

@app.route('/properties/create', methods=['POST', 'GET'])
def create_properties():
    
    form = PropertyForm()

    if request.method == 'POST':
        try:
            if form.validate_on_submit():
                title = form.prop_title.data
                descript = form.descript.data
                room_no = form.room_no.data
                bath_no = form.bath_no.data
                price = form.price.data
                type = form.prop_type.data
                local = form.location.data
                img = form.photofile.data
                if img:
                    filename = secure_filename(img.filename)
                    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    flash('Please upload an image for the property', 'error')
                    return redirect(request.url)

                
                new_prop =  Propertymod(title, descript, room_no, bath_no, price, type, local, filename)
                db.session.add(new_prop)
                db.session.commit()

                flash('Property Added', 'success')
                return redirect(url_for('properties'))
            else:
                flash_errors(form)
              
        except Exception as e:
            # Handle any exceptions here
            flash({'An error occurred' : str(e)}, 400)

    return render_template('addproperty.html', form=form)


@app.route('/properties', methods=['GET'])
def properties():
    try:
        return render_template('properties_listing.html', properties=Propertymod.query.all())
    except Exception as e:
        flash({'An error occurred': str(e)}, 400)
    


@app.route('/properties/<propertyid>', methods = ['GET'])
def view_properties(propertyid):

    try:
        prop_id = Propertymod.query.filter_by(id=propertyid).first()
        return render_template('property_details.html', property = prop_id)
    
    except Exception as e:
        flash({'An error occurred' : str(e)}, 400)


@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)



def get_uploaded_images():
    rootdir =os.getcwd()
    file_lst=[]
    # print("root directry:",rootdir)
    for subdir, dirs, files in os.walk(rootdir + 'uploads/'):
        for file in files:
            file_lst.append(os.path.join(subdir, file))
    return file_lst



###
# The functions below should be applicable to all Flask apps.
###

# Display Flask WTF errors as Flash messages
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
