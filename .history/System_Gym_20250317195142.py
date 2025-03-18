import mysql.connector
from mysql.connector import pooling
from abc import ABC, abstractmethod
from datetime import date

# Clase para manejar el pool de conexiones
class Conexion:
    _pool = None
    
    @classmethod
    def obtener_conexion(cls):
        if cls._pool is None:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=5,
                host="localhost",
                user="root",
                password="tu_contraseña",
                database="gym_db"
            )
        return cls._pool.get_connection()

# Clase abstracta Persona
class Persona(ABC):
    def __init__(self, nombre, apellido, telefono, correo):
        self._nombre = nombre
        self._apellido = apellido
        self._telefono = telefono
        self._correo = correo
    
    @abstractmethod
    def guardar(self):
        pass

# Clase Cliente
class Cliente(Persona):
    def __init__(self, nombre, apellido, telefono, correo, membresia, id_cliente=None):
        super().__init__(nombre, apellido, telefono, correo)
        self._id_cliente = id_cliente
        self._membresia = membresia
    
    def guardar(self):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO clientes (nombre, apellido, telefono, correo, membresia) VALUES (%s, %s, %s, %s, %s)"
            valores = (self._nombre, self._apellido, self._telefono, self._correo, self._membresia)
            cursor.execute(sql, valores)
            conexion.commit()
        conexion.close()
    
    @classmethod
    def obtener_cliente(cls, correo):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM clientes WHERE correo = %s"
            cursor.execute(sql, (correo,))
            return cursor.fetchone()

# Clase Producto
class Producto:
    def __init__(self, nombre_prodto, precio_unid, id_producto=None):
        self._id_producto = id_producto
        self._nombre_prodto = nombre_prodto
        self._precio_unid = precio_unid
    
    def guardar_producto(self):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO productos (nombre_prodto, precio_unid) VALUES (%s, %s)"
            cursor.execute(sql, (self._nombre_prodto, self._precio_unid))
            conexion.commit()
        conexion.close()

# Clase Comprar
class Comprar:
    def __init__(self):
        self.id_compra = None
        self.id_cliente = None
        self.fecha_compra = date.today()
        self.total_pagado = 0.0
        self.forma_pago = None
        self.carrito_compras = []
    
    def obtener_precio_unid(self, id_producto):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "SELECT precio_unid FROM productos WHERE id_producto = %s"
            cursor.execute(sql, (id_producto,))
            resultado = cursor.fetchone()
        conexion.close()
        return resultado[0] if resultado else None
    
    def agregar_producto(self, id_producto, cantidad):
        precio_unid = self.obtener_precio_unid(id_producto)
        if precio_unid:
            self.carrito_compras.append((id_producto, cantidad, precio_unid))
            self.total_pagado += cantidad * precio_unid
        else:
            print("Producto no encontrado.")
    
    def guardar_compra(self, correo, forma_pago):
        cliente = Cliente.obtener_cliente(correo)
        if not cliente:
            print("Cliente no encontrado.")
            return
        self.id_cliente = cliente["id_cliente"]
        self.forma_pago = forma_pago
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO compras (id_cliente, fecha_compra, total_pagado, forma_pago) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.id_cliente, self.fecha_compra, self.total_pagado, self.forma_pago))
            self.id_compra = cursor.lastrowid
            for producto in self.carrito_compras:
                sql_detalle = "INSERT INTO detalles_compra (id_compra, id_producto, cantidad, precio_final) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_detalle, (self.id_compra, *producto))
            conexion.commit()
        conexion.close()

# Métodos adicionales para consultas
class Consultas:
    @staticmethod
    def productos_mas_vendidos():
        conexion = Conexion.obtener_conexion()
        with conexion.cursor(dictionary=True) as cursor:
            sql = "SELECT p.nombre_prodto, SUM(dc.cantidad) as total_vendido FROM detalles_compra dc JOIN productos p ON dc.id_producto = p.id_producto GROUP BY p.nombre_prodto ORDER BY total_vendido DESC"
            cursor.execute(sql)
            resultados = cursor.fetchall()
            for producto in resultados:
                print(f"Producto: {producto['nombre_prodto']}\nTotal Vendido: {producto['total_vendido']}\n")
    
    @staticmethod
    def ver_compras_cliente(correo):
        cliente = Cliente.obtener_cliente(correo)
        if not cliente:
            print("Cliente no encontrado.")
            return
        id_cliente = cliente["id_cliente"]
        conexion = Conexion.obtener_conexion()
        with conexion.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM compras WHERE id_cliente = %s"
            cursor.execute(sql, (id_cliente,))
            compras = cursor.fetchall()
            for compra in compras:
                print(f"Compra ID: {compra['id_compra']}, Fecha: {compra['fecha_compra']}, Total Pagado: {compra['total_pagado']}, Forma de Pago: {compra['forma_pago']}")

# Menú principal
if __name__ == "__main__":
    while True:
        print("\n--- GESTIÓN GYM ---")
        print("1. Registrar Cliente")
        print("2. Registrar Producto")
        print("3. Comprar")
        print("4. Ver información del Cliente")
        print("5. Ver compras del Cliente")
        print("7. Productos más Vendidos")
        print("8. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "4":
            correo = input("Correo del Cliente: ")
            print(Cliente.obtener_cliente(correo))
        elif opcion == "5":
            correo = input("Correo del Cliente: ")
            Consultas.ver_compras_cliente(correo)
        elif opcion == "7":
            Consultas.productos_mas_vendidos()
        elif opcion == "8":
            print("Saliendo...")
            break
        else:
            print("Opción aún no implementada.")
