from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
import mysql.connector

app = Flask(__name__)

# CODE LOGIN INICIO
app.secret_key = 'tu_clave_secreta'  # Necesario para usar sesiones

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="As1234$",
    database="reseller"
)
cursor = db.cursor(dictionary=True)

# Lista fija de meses
MESES = [
    ("01", "Enero"), ("02", "Febrero"), ("03", "Marzo"),
    ("04", "Abril"), ("05", "Mayo"), ("06", "Junio"),
    ("07", "Julio"), ("08", "Agosto"), ("09", "Septiembre"),
    ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre")
]


@app.route('/')
def home():
    if 'usuario' in session:
        cursor.execute("SELECT * FROM cuentas")  # tabla principal
        users = cursor.fetchall()
        return render_template('index.html', users=users, meses=MESES)
    else:
        return redirect(url_for('login'))
    

""" @app.route('/index')
def index():
    cursor.execute("SELECT * FROM cuentas")
    cuentasb = cursor.fetchall()
    return render_template('index.html', users=cuentasb, meses=MESES) """

@app.route('/index', methods=['GET', 'POST'])
def index():
    cuentasb = []
    mes_seleccionado = None

    if request.method == 'POST':
        mes_seleccionado = request.form['mes']
        
        if mes_seleccionado == "all":
            # 🔹 Sin filtro, todos los registros
            cursor.execute("SELECT * FROM cuentas")
            cuentasb = cursor.fetchall()
        else:
            # 🔹 Filtro por mes
            query = """
                SELECT * 
                FROM cuentas
                WHERE DATE_FORMAT(fecha_reg, '%m') = %s
            """
            cursor.execute(query, (mes_seleccionado,))
            cuentasb = cursor.fetchall()
            
    else:
        # Cargar todos por defecto
        cursor.execute("SELECT * FROM cuentas")
        cuentasb = cursor.fetchall()

    return render_template(
        'index.html',
        users=cuentasb,
        meses=MESES,
        mes_seleccionado=mes_seleccionado
    )
    

# DEF LOGIN INICIO

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("""
            SELECT * FROM usuarios 
            WHERE user = %s AND pass = %s AND estado = 'activo'
        """, (username, password))
        user = cursor.fetchone()

        if user:
            session['usuario'] = user['user'] 
            session['rol'] = user['rol']
            return redirect(url_for('home'))
        else:
            return "Usuario o contraseña incorrectos o cuenta inactiva"
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

  # DEF LOGIN FIN  


@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        dominio = request.form['dominio']
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        quota = float(request.form['quota'])
       # quota = request.form['quota']
        fecha_actual = date.today()
        try:
            cursor.execute("INSERT INTO cuentas (dominio, usuario, contrasena, quota, fecha_reg) VALUES (%s, %s, %s, %s)", (dominio, usuario, contrasena, quota, fecha_actual))
            db.commit()
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            print(f"Error al agregar usuario: {err}")
            return "Ocurrió un error al agregar el usuario."
    return render_template('add.html')

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        dominio = request.form['dominio']
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        fecha_reg = request.form.get('fecha_reg')
        disco = request.form['disco']
        transfer_mensual = request.form['transfer_mensual']
        paquete = request.form['paquete']
        precio = request.form['precio']
        server1 = request.form['server1']
        server2 = request.form['server2']
        detalle = request.form['detalle']
        estado = request.form['estado']
        try:
            cursor.execute("INSERT INTO cuentas (dominio, usuario, contrasena, fecha_reg, disco, transfer_mensual, paquete, precio, server1, server2, detalle, estado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (dominio, usuario, contrasena, fecha_reg, disco, transfer_mensual, paquete, precio, server1, server2, detalle, estado))
            db.commit()
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            print(f"Error al agregar usuario: {err}")
            return "Ocurrió un error al agregar el usuario."
    return render_template('add_account.html')


@app.route('/detail/<int:id>', methods=['GET', 'POST'])
def detail_user(id):

    user = None
    try:
        if request.method == 'POST':
            id = request.form['id']


            cursor.execute("SELECT * FROM cuentas WHERE ID = id")
            db.commit()
            return redirect(url_for('detail'))

        cursor.execute("SELECT id, dominio, usuario, contrasena, disco, transfer_mensual, paquete, precio, server1, server2, detalle, estado, DATE_FORMAT(fecha_reg, '%Y-%m-%d') AS fecha_reg FROM cuentas WHERE id = %s", (id,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error al editar usuario: {err}")
        return "Ocurrió un error al editar el usuario."
    if user:
        return render_template('detail.html', user=user)
    return "Usuario no encontrado."



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'usuario' not in session or session.get('rol') != 'administrador':
        return "Acceso denegado. Solo administradores pueden editar."
    
    user = None
    try:
        if request.method == 'POST':
            dominio = request.form['dominio']
            usuario = request.form['usuario']
            contrasena = request.form['contrasena']
            fecha_reg = request.form.get('fecha_reg')
            disco = request.form['disco']
            transfer_mensual = request.form['transfer_mensual']
            paquete = request.form['paquete']
            precio = request.form['precio']
            server1 = request.form['server1']
            server2 = request.form['server2']
            detalle = request.form['detalle']
            estado = request.form['estado']

            cursor.execute("UPDATE cuentas SET dominio = %s, usuario = %s, contrasena = %s, fecha_reg = %s, disco = %s, transfer_mensual = %s, paquete = %s, precio = %s, server1 = %s, server2 = %s, detalle = %s, estado = %s WHERE id = %s", (dominio, usuario, contrasena, fecha_reg, disco, transfer_mensual, paquete, precio, server1, server2, detalle, estado, id))
            db.commit()
            return redirect(url_for('index'))

        cursor.execute("SELECT id, dominio, usuario, contrasena, disco, transfer_mensual, paquete, precio, server1, server2, detalle, estado, DATE_FORMAT(fecha_reg, '%Y-%m-%d') AS fecha_reg FROM cuentas WHERE id = %s", (id,))
        user = cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error al editar usuario: {err}")
        return "Ocurrió un error al editar el usuario."
    if user:
        return render_template('edit.html', user=user)
    return "Usuario no encontrado."


@app.route('/delete/<int:id>')
def delete_user(id):
    try:
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        db.commit()
        return redirect(url_for('index'))
    except mysql.connector.Error as err:
        print(f"Error al eliminar usuario: {err}")
        return "Ocurrió un error al eliminar el usuario." # O renderizar una plantilla de error

@app.route('/delete_account/<int:id>')
def delete_account(id):
    try:
        cursor.execute("DELETE FROM cuentas WHERE id = %s", (id,))
        db.commit()
        return redirect(url_for('index'))
    except mysql.connector.Error as err:
        print(f"Error al eliminar usuario: {err}")
        return "Ocurrió un error al eliminar el usuario." # O renderizar una plantilla de error
    
# Código para Buscador

@app.route('/cuentas', methods=['POST'])
def cuentas():
    mes = request.form['mes']

    # 🔹 Consulta registros por mes
    query = """
        SELECT * 
        FROM cuentas
        WHERE DATE_FORMAT(fecha_reg, '%m') = %s
    """
    cursor.execute(query, (mes,))
    registros = cursor.fetchall()

    return render_template("cuentas.html", registros=registros, mes=mes)


# Ejecuta directamente el archivo app.py como un script de Python.
# Requiere que dentro de app.py esté esto al final:

# if __name__ == '__main__':
#     app.run(debug=True)
