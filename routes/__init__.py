
from flask import  render_template, request, redirect, session, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import app, db

from schemas.models import probikini, Users


@app.route("/")
def index():
    return render_template('base.html')


@app.route('/add', methods=['POST'] )
def add_product_to_cart():
    try:
        _quantity = int(request.form['quantity'])
        code = request.form['code']
        category = request.form['category']
        categorySinEspacio = category[1:]
        codeSinEspacio = code[1:]

        #print("categorySinEspacio:",categorySinEspacio)
        #print("codeSinEspacio:",codeSinEspacio)
        #validar los valores recibidos
        if _quantity and category and request.method == 'POST':

            probikiniItem = probikini.query.filter(probikini.code == codeSinEspacio).first()
            if probikiniItem == None :
                print("No se encontro codigo: ")
            #print("Codigo: ", probikiniItem.code)
            #print("Nombre: ", probikiniItem.nombre)

            itemArray = { probikiniItem.code : {'nombre' : probikiniItem.nombre, 'code' : probikiniItem.code, 'quantity' : _quantity, 'price' : probikiniItem.price, 'image' : probikiniItem.image, 'total_price': _quantity * probikiniItem.price}}

            all_total_price = 0
            all_total_quantity = 0

            session.modified = True
            if 'cart_item' in session:
                if probikiniItem.code in session['cart_item']:
                    for key, value in session['cart_item'].items():
                        if probikiniItem.code == key:
                            old_quantity = session['cart_item'] [key] ['quantity']
                            total_quantity = old_quantity + _quantity

                            session['cart_item'][key]['quantity'] = total_quantity
                            session['cart_item'][key]['total_price'] = total_quantity * probikiniItem.price
                else:
                    session['cart_item'] = array_merge(session['cart_item'], itemArray)

                for key, value in session['cart_item'].items():
                    individual_quantity = int(session['cart_item'][key]['quantity'])
                    individual_price = float(session['cart_item'][key]['total_price'])
                    all_total_quantity = all_total_quantity + individual_quantity
                    all_total_price = all_total_price + individual_price


            else:
                session['cart_item'] = itemArray
                all_total_quantity = all_total_quantity + _quantity
                all_total_price = all_total_price + _quantity * probikiniItem.price

            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

            return redirect(url_for('.products'))
        else:
            flash('Error al agregar articulo al carrito')

    except Exception as e:
        print(e)
    finally:
        db.session.close()


@app.route('/products', methods=['POST','GET'] )
def products():
    products = db.session.query(probikini).filter(probikini.category == 'accesorios')

    #products = db.session.execute(db.select(probikini).order_by(probikini.id)).scalars()
    db.session.commit()

    return render_template('products.html' , products=products )


@app.route('/empty')
def empty_cart():
    try:
        session.clear()
        return redirect(url_for('products'))
    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True

        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break
        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        return redirect(url_for('products'))
    except Exception as e:
        print(e)


def array_merge( first_array , second_array):
    if isinstance(first_array, list) and isinstance(second_array, list ):
        return first_array + second_array
    elif isinstance( first_array, dict) and isinstance (second_array, dict):
        return dict( list( first_array.items()) + list(second_array.items()))
    elif isinstance(first_array, set) and isinstance( second_array, set):
        return first_array.union(second_array)
    return False 


@app.route('/enterizos')
def enterizos():
    products = db.session.query(probikini).filter(probikini.category == 'enterizos')
    db.session.commit()
    return render_template('enterizos.html', products=products )


@app.route('/bikinis', methods = ['GET', 'POST'] )
def bikinis():
    products = db.session.query(probikini).filter(probikini.category == 'bikinis')
    db.session.commit()
    return render_template('bikinis.html', products=products )


@app.route('/accesorios', methods=['POST','GET'])
def accesorios():
    products = db.session.query(probikini).filter(probikini.category == 'accesorios')
    db.session.commit()
    return render_template('accesorios.html', products=products )


@app.route('/registrarse', methods = ['GET','POST'])
def registrarse():
    if request.method == 'POST':

#primero vamos a cifrar la contrasena que entra por el formulario para despues guardarla en la bd
        hashed_pw = generate_password_hash(request.form['contrasena'], method='sha256') #el primer paramentro va hacer laa cadena q va a cifrar, tenemos q recuperar el dato q se ingreso en el formulario(lo nombramos name={.....}), el segnd paramt es el metodo con el cual vamos a cifrar la contrasena.
#construir el objeto q vamos a almacenar en la bd, creamos una nueva variable y vamos a rellenar los campos de la tabla.
        new_user = Users(correo=request.form['correo'], contrasena= hashed_pw) # el id se incrementa solo asi q vamos a pasarle el correo y contrasena, nuestra contras va a equivaler a nuestra contras haseada.
# anadirlo a la base d datos, le pasamos el nuevo objeto q es new_user
        db.session.add(new_user)
        db.session.commit() #confirmamos cada uno de los cambios escritos en la dase d datos
        flash('Te has registrado exitosamente! ', 'success') #con success(el segundo parametro en flash) sirve para darle estilo en css.
        flash('Verifica iniciando sesion.', 'warning')
        return redirect(url_for('login')) #'Registro exitoso!'
    return render_template('registrarse.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
#si el metodo es get va a devolver la plantilla login.html, si es post va hacer lo siguiente
    if request.method == 'POST':
        user = Users.query.filter_by(correo = request.form['correo']).first() #aqui vamos a almacenar el resultado de nuestra consulta, le decimos q tome el primero q encuentre
#luego vamos a ver si el usuario coicide con la contrasena q tiene relacionada.
        if user and check_password_hash(user.contrasena, request.form['contrasena'] ): # comparamos con el que esta en la base de datos com ya tenemos el usuario, si es q
#encontro  el usuario deberiamos de tener el objeto y el objeto tiene el atributo contrasena, y luego el dato del formulario,. est afuncion los va a comparar.
            session['correo'] = user.correo
            #flash ('ya estas registrado', 'success')
            return redirect(url_for('.index'))
        else:
            flash ('tus datos son incorrectos, vuelve a intentarlo.', 'error')


    return render_template('login.html')


@app.before_request
def before_request():
    if 'correo' in session:
        g.user = session['correo']
    else:
        g.user = None

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
