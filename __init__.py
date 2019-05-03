from flask import Flask, render_template, url_for, flash, redirect, request, session, make_response, send_file
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart
from functools import wraps
from datetime import datetime, timedelta
import gc
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from werkzeug.utils import secure_filename
from content import Content
from db_connect import connection 

UPLOAD_FOLDER = "/var/www/FlaskApp/FlaskApp/uploads"

ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Please login.")
            return redirect(url_for('login'))
    return wrap

APP_CONTENT = Content()

@app.route("/")
def hello():
    return render_template("main.html")

@login_required
@app.route("/dashboard/")
def dashboard():
    try:
        return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)
    
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    try:
        c, conn = connection()
        if request.method == "POST":
            
            data = c.execute("SELECT * FROM users WHERE username = ('{0}')". format(thwart(request.form['username'])))
            
            data = c.fetchone()[2]
            
            if sha256_crypt.verify(request.form["password"], data):
                session['logged in'] = True
                session['username'] = request.form['username']
                
                flash("You are now logged in! "+session['username']+"!")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid credentials, try again."
                
        return render_template("login.html", error = error)
    except Exception as e:
        flash(e)
        error = "Invalid creditials, try again."
        return render_template("login.html", error = error)

@login_required
@app.route("/logout/")
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('index'))

class RegistrationForm(Form):
    username = TextField("Username", [validators.Length(min=4, max=20)])
    email = TextField("Email Address", [validators.Length(min=6, max=50)])
    password = PasswordField("New Password", [validators.Required(),
                                             validators.EqualTo('confirm', 
                                             message="Passwords must match")])
    confirm = PasswordField("Repeat Password")
    accept_tos = BooleanField("I accept the Terms of Service and Privacy Notice", [validators.Required()])
    

@app.route('/register/', methods=["GET", "POST"])
def register_page():
   
    try:
        form = RegistrationForm(request.form)
        
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
        
            c, conn = connection() #if it runs, it will post a string
        
            x = c.execute("SELECT * FROM users WHERE username = ('{0}')".format((thwart(username))))
            
            if int(x) > 0:
                flash("That username is already taken, please choose another.")
                return render_template("register.html", form = form)
            else:
                c.execute("INSERT INTO users (username,password,email,tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username), thwart(password), thwart(email), thwart("/dashboard/")))
                
                conn.commit()
                flash("Thanks for registering, " +username+"!")
                conn.close()
                gc.collect()
                
                session['logged_in'] = True
                session['username'] = username
                
                return redirect(url_for('dashboard'))
        return render_template("register.html", form = form)
            
    except Exception as e:
            return(str(e)) # remember to remove! For debugging only!
        
    return("Connected")

@app.route('/welcome/')
def welcome_to_jinja():
    try:
        #This is where all the python goes!
        
        def my_function():
            output = ["DIGIT 400 is good", "Python, Java, php, SQL, C++","<p><strong>hello world!</strong><p>", 42, "42"]
            return output
        
        output = my_function()
        
        return render_template("templating_demo.html", output = output)
    except Exception as e:
        return str(e)
    
@app.route("/uploads/", methods=["GET", "POST"])
@login_required
def upload_file():
    try:
        if request.method == "POST":
            if "file" not in request.files:
                flash("No file part")
                return redirect(request.url)
            file = request.files["file"]
            
            if file.filename == "":
                flash("No selected file")
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                flash("File" +str(filename) + "upload successful!")
                return render_template('uploads.html', filename = filename)
            return render_template("uploads.html")            
    except Exception as e:
        return str(e) # remove for production
    
    
@app.route("/download/")
@login_required
def downloads():
    try:
        return send_file("/var/www/FlaskApp/FlaskApp/uploads/dog.jpeg",
        attachment_filename+"doggie.jpeg")
    except Exception as e:
        return str(e)

@app.route("/kennels/")
def kennels():
    try:
        return render_template("kennels.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)
    
@app.route("/animal_hospitals/")
def animal_hospitals():
    try:
        return render_template("animal_hospitals.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)

@app.route("/pet_training/")
def pet_training():
    try:
        return render_template("pet_training.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)
    
@app.route("/pet_grooming/")
def pet_grooming():
    try:
        return render_template("pet_grooming.html", APP_CONTENT = APP_CONTENT)
    except Exception as e:
        return render_template("500.html", error = e)
    

## Site Map

@app.route('/sitemap.xml/', methods=["GET"])
def sitemap():
    try:
        page = []
        week = (datetime.now() - timedelta(days = 7)).date().isoformat()
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments)==0:
                page.append(["https://digit400.party"+str(rule.rule),week])
        
        sitemap_xml = render_template('sitemap_template.xml', page = page)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
        
        
    except Exception as e:
        return(str(e))
@app.route("/robots.txt")
def robots():
    return("User-agent: \nDisallow: /login \nDisallow: /register")

## Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")

@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html", error = e)

if __name__ == "__main__":
    app.run() # should be turned off/False for production!
