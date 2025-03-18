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
                password="admin",
                database="gym_db"
            )
        return cls._pool.get_connection()

# Clase abstracta Persona
class Persona(ABC):
    def _init_(self, nombre, apellido, telefono, correo):
        self._nombre = nombre
        self._apellido = apellido
        self._telefono = telefono
        self._correo = correo
    
    @abstractmethod
    def guardar(self):
        pass

# Clase Cliente
class Cliente(Persona):
    def _init_(self, nombre, apellido, telefono, correo, membresia, id_cliente=None):
        super()._init_(nombre, apellido, telefono, correo)
        self._id_cliente = id_cliente
        self._membresia = membresia
    
    def guardar(self):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO clientes (nombre, apellido, telefono, correo, membresia) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (self._nombre, self._apellido, self._telefono, self._correo, self._membresia))
            conexion.commit()
        conexion.close()
    
    @classmethod
    def obtener_cliente(cls, correo):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM clientes WHERE correo = %s"
            cursor.execute(sql, (correo,))
            return cursor.fetchone()
        conexion.close()

# Clase Producto
class Producto:
    def _init_(self, nombre_prodto, precio_unid):
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
    def _init_(self, correo):
        self.id_cliente = self.obtener_id_cliente(correo)
        self.total_pagado = 0
        self.carrito_compras = []
    
    def obtener_id_cliente(self, correo):
        cliente = Cliente.obtener_cliente(correo)
        return cliente["id_cliente"] if cliente else None
    
    def agregar_producto(self, id_producto, cantidad):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "SELECT precio_unid FROM productos WHERE id_producto = %s"
            cursor.execute(sql, (id_producto,))
            resultado = cursor.fetchone()
        conexion.close()
        
        if resultado:
            precio_unid = resultado[0]
            self.carrito_compras.append((id_producto, cantidad, precio_unid))
            self.total_pagado += cantidad * precio_unid
        else:
            print("Producto no encontrado.")
    
    def guardar_compra(self, forma_pago):
        if not self.id_cliente:
            print("Cliente no encontrado.")
            return
        
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO compras (id_cliente, fecha_compra, total_pagado, forma_pago) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.id_cliente, date.today(), self.total_pagado, forma_pago))
            id_compra = cursor.lastrowid
            for producto in self.carrito_compras:
                sql_detalle = "INSERT INTO detalles_compra (id_compra, id_producto, cantidad, precio_final) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_detalle, (id_compra, *producto))
            conexion.commit()
        conexion.close()

# Clase Consultas
class Consultas:
    @staticmethod
    def ver_compras_cliente(correo):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor(dictionary=True) as cursor:
            sql = "SELECT * FROM compras WHERE id_cliente = (SELECT id_cliente FROM clientes WHERE correo = %s)"
            cursor.execute(sql, (correo,))
            for compra in cursor.fetchall():
                print(compra)
        conexion.close()
    
    @staticmethod
    def productos_mas_vendidos():
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "SELECT id_producto, SUM(cantidad) as total FROM detalles_compra GROUP BY id_producto ORDER BY total DESC"
            cursor.execute(sql)
            for producto in cursor.fetchall():
                print(producto)
        conexion.close()

# Menú principal
if _name_ == "_main_":
    while True:
        print("\n--- GESTIÓN GYM ---")
        print("1. Registrar Cliente")
        print("2. Registrar Producto")
        print("3. Comprar")
        print("4. Ver información del Cliente")
        print("5. Ver compras del Cliente")
        print("6. Ver todas las compras")
        print("7. Productos más Vendidos")
        print("8. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            telefono = input("Teléfono: ")
            correo = input("Correo: ")
            membresia = input("Membresía: ")
            Cliente(nombre, apellido, telefono, correo, membresia).guardar()
        elif opcion == "2":
            nombre_prodto = input("Nombre del Producto: ")
            precio_unid = float(input("Precio: "))
            Producto(nombre_prodto, precio_unid).guardar_producto()
        elif opcion == "3":
            correo = input("Correo del Cliente: ")
            compra = Comprar(correo)
            while True:
                id_producto = input("ID Producto: ")
                cantidad = int(input("Cantidad: "))
                compra.agregar_producto(id_producto, cantidad)
                if input("¿Agregar otro producto? (s/n): ") != "s":
                    break
            forma_pago = input("Forma de Pago: ")
            compra.guardar_compra(forma_pago)
        elif opcion == "4":
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
            print("Opción inválida.")