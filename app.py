from flask import Flask,request,render_template,redirect,session,url_for,flash
from database import get_db_connection, database
import hashlib
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

# random 24 char session no generation
app.secret_key = os.urandom(24)
# uploads file and check if uploaded file is image or not
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# FUNCTIONS
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route("/")
def root():
    try:
        database()

    except Exception as e:
        return render_template("error.html",info=e)
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/adduser", methods=["POST"])
def adduser():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    conf_password = request.form.get("conf_password")
    address = request.form.get("address")
    contact = request.form.get("phone_no")
    hashed_password = hash_password(password)
    try:
        # Establish database connection
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM credential WHERE EMAIL = %s", (email,))
                if cursor.fetchone():
                    raise ValueError("Email already registered")
                if conf_password != password:
                    raise ValueError("Password and confirm password don't match")
                cursor.execute(
                    "INSERT INTO credential(USERNAME, EMAIL, PASSWORD, Role, address, contact) VALUES (%s, %s, %s, %s, %s, %s)",
                    (username, email, hashed_password, "user", address, contact),
                )
        return redirect("/")
    except Exception as e:
        return render_template("register.html", info=e)

@app.route("/signin", methods=["POST"])
def login():

    email = request.form.get("email")
    password = request.form.get("password")
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM credential WHERE EMAIL = %s", (email,))
                user = cursor.fetchone()
                if user and verify_password(user[3], password):
                    session["user_id"] = user[0]
                    session["role"] = user[6]
                    session["username"] = user[1]
                    return redirect("/home")
    except Exception as e:
        return render_template("error.html", info=str(e))

    return render_template("login.html", info="Invalid email or password")

@app.route("/home" ,methods=["Get"])
def home():
    email=request.form.get("email")
    password=request.form.get("password")
    print(email,password)
    return render_template("homepage.html")

@app.route("/products")
def products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("products.html" , products=products)

@app.route("/contact")
def contact():
    return render_template("contact.html")                           
@app.route("/add", methods=('GET', 'POST'))
def add():
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            stock = request.form['stock']
            if 'image' not in request.files:
                return redirect(request.url)
            file = request.files['image']
            if file.filename == '':
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('INSERT INTO products (name, description, price, stock,image_filename) VALUES (%s, %s, %s, %s, %s)',
                        (name, description, price, stock,filename))
            conn.commit()
            cur.close()
            conn.close()

            return redirect(url_for('adminproducts'))

        return render_template('add_products.html')             

@app.route("/adminproducts")
def adminproducts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM products;')
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin_productlist.html', products=products)


@app.route('/update/<int:item_id>', methods=['GET', 'POST'])
def update(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']

        image_file = request.files['image']
        image_filename = None

        if image_file and allowed_file(image_file.filename):
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        if image_filename:
            cursor.execute(
            """
                UPDATE products
                SET name = %s, description = %s, price = %s, stock = %s, image_filename = %s
                WHERE id = %s
            """,
                (name, description, price, stock, image_filename, item_id),
            )
        else:
            cursor.execute(
                """
                UPDATE products
                SET name = %s, description = %s, price = %s, stock = %s
                WHERE id = %s
            """,
                (name, description, price, stock, item_id),
            )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Product updated successfully!', 'success')
        return redirect(url_for('adminproducts'))

    cursor.execute('SELECT * FROM products WHERE id = %s', (item_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if product is None:
        flash('Product not found!', 'error')
        return redirect(url_for('adminproducts'))

    return render_template('update.html', product=product)


@app.route('/delete/<int:item_id>', methods=['GET'])
def delete(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = %s', (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('adminproducts'))

@app.route("/logout")
def logout():
    return redirect("/")                         

if __name__ == "__main__":
    app.run(debug=False)
