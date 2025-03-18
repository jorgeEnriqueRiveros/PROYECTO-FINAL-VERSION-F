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
                password="123456",
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
    
    @property
    def nombre(self):
        return self._nombre
    
    @property
    def apellido(self):
        return self._apellido
    
    @property
    def telefono(self):
        return self._telefono
    
    @property
    def correo(self):
        return self._correo
    
    @abstractmethod
    def guardar(self):
        pass

# Clase Cliente
class Cliente(Persona):
    def __init__(self, nombre, apellido, telefono, correo, membresia, id_cliente=None):
        super().__init__(nombre, apellido, telefono, correo)
        self._id_cliente = id_cliente
        self._membresia = membresia
    
    @property
    def id_cliente(self):
        return self._id_cliente
    
    @property
    def membresia(self):
        return self._membresia
    
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
    
    @property
    def id_producto(self):
        return self._id_producto
    
    @property
    def nombre_prodto(self):
        return self._nombre_prodto
    
    @property
    def precio_unid(self):
        return self._precio_unid
    
    def guardar_producto(self):
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO productos (nombre_prodto, precio_unid) VALUES (%s, %s)"
            cursor.execute(sql, (self._nombre_prodto, self._precio_unid))
            conexion.commit()
        conexion.close()

# Clase Comprar
class Comprar:
    def __init__(self, correo):
        self.id_compra = None
        self.id_cliente = self.obtener_id_cliente(correo)
        self.fecha_compra = None
        self.total_pagado = None
        self.forma_pago = None
        self.carrito_compras = []
    
    def obtener_id_cliente(self, correo):
        cliente = Cliente.obtener_cliente(correo)
        return cliente["id_cliente"] if cliente else None
    
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
            self.total_pagado = (self.total_pagado or 0) + cantidad * precio_unid
        else:
            print("Producto no encontrado.")
    
    def guardar_compra(self, forma_pago):
        if not self.id_cliente:
            print("Cliente no encontrado.")
            return
        self.forma_pago = forma_pago
        conexion = Conexion.obtener_conexion()
        with conexion.cursor() as cursor:
            sql = "INSERT INTO compras (id_cliente, fecha_compra, total_pagado, forma_pago) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (self.id_cliente, date.today(), self.total_pagado, self.forma_pago))
            self.id_compra = cursor.lastrowid
            for producto in self.carrito_compras:
                sql_detalle = "INSERT INTO detalles_compra (id_compra, id_producto, cantidad, precio_final) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_detalle, (self.id_compra, *producto))
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
if __name__ == "__main__":
    while True:
        print("\n--- GESTIÓN GYM ---")
        print("1. Registrar Cliente")
        print("2. Registrar Producto")
        print("3. Comprar")
        print("4. Ver información del Cliente")
        print("5. Ver compras del Cliente")
        print("6. Modificar Cliente")
        print("7. Productos más Vendidos")
        print("8. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            nombre = input("Nombre: ")
            apellido = input("Apellido: ")
            telefono = input("Teléfono: ")
            correo = input("Correo: ")
            membresia = input("Tipo de membresía: ")
            nuevo_cliente = Cliente(nombre, apellido, telefono, correo, membresia)
            nuevo_cliente.guardar()
            print("Cliente registrado con éxito.")
        elif opcion == "2":
            nombre_prodto = input("Nombre del producto: ")
            precio_unid = float(input("Precio por unidad: "))
            nuevo_producto = Producto(nombre_prodto, precio_unid)
            nuevo_producto.guardar_producto()
            print("Producto registrado con éxito.")
            
        elif opcion == "4":
            correo = input("Ingrese el correo del cliente: ")
            cliente = Cliente.obtener_cliente(correo)
            print(cliente if cliente else "Cliente no encontrado.")
        elif opcion == "5":
            print("Opción aún no implementada.")
        elif opcion == "6":
            correo = input("Correo del cliente a modificar: ")
            telefono = input("Nuevo teléfono: ")
            membresia = input("Nueva membresía: ")
            Cliente.modificar_cliente(correo, telefono, membresia)
            print("Cliente modificado con éxito.")
        elif opcion == "7":
            productos = Producto.productos_mas_vendidos()
            for producto in productos:
                print(f"{producto[0]} - Vendidos: {producto[1]}")
        elif opcion == "8":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")