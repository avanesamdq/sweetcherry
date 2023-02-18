from __init__ import db 

#sqlalchemy nos permite crear a partir de clases de python
class Users(db.Model): 
    id = db.Column(db.Integer, primary_key = True)
    correo = db.Column(db.String(60), unique = True, nullable = False)
    contrasena = db.Column(db.String(88), nullable = False)


class probikini(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    code = db.Column(db.String(225))
    nombre = db.Column(db.String(45))
    image = db.Column(db.String(225))
    category = db.Column(db.String(70))
    price = db.Column(db.Integer)
    discount = db.Column(db.Integer)

    def __init__(self, code, nombre, image, category, price, discount) -> None:
        self.code = code
        self.nombre = nombre
        self.image = image
        self.category = category
        self.price = price
        self.discount = discount
