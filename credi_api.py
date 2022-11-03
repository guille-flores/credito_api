try:
    import datetime
    from flask import Flask, jsonify
    import psycopg2
except ImportError as eImp:
  print(f"There was an error importing the next libraries: {eImp}")


#entrada
primer_nombre = "Maria" #@param {type: "string"}
apellido_paterno = "Gonzalez" #@param {type: "string"}
apellido_materno = "Carral" #@param {type: "string"}
fecha_nacimiento = "15-01-1962" #@param {type: "date"}
ingreso_mensual = 15000  #@param {type: "number"}
dependientes = 0  #@param {type: "integer"}



if ingreso_mensual < 0:
   print('El ingreso mensual registrado es negativo ('+ str(ingreso_mensual) +'). Utilizaremos el valor positivo para tu registro y evaluación dew crédito',)
if dependientes < 0:
  print('El número de dependientes económicos registrado es negativo  ('+ str(dependientes) +'). Utilizaremos el valor positivo para tu registro y evaluación dew crédito')

usuario = {
    "name": primer_nombre, 
    "fath_lastname": apellido_paterno, 
    "moth_lastname": apellido_materno,
    "nacimiento": fecha_nacimiento,
    "rfc": "",
    "ingreso_men": abs(ingreso_mensual),
    "dependientes": abs(dependientes),
    "aprobar" : False
      }

#para la creacion del RFC vamos a trabajr con la fecha de nacimiento como un dataframe por comodidad
fecha_nacimiento = datetime.datetime.strptime(usuario["nacimiento"], '%d-%m-%Y')
date2str = lambda x : "0"+str(x) if (x<10) else x #para agregar 0 en caso de que el mes o dia sean menores a 10.
usuario["rfc"] = (usuario["fath_lastname"][0:2]+usuario["moth_lastname"][0]+usuario["name"][0]+str(fecha_nacimiento.year)[2:]+str(date2str(fecha_nacimiento.month))+str(date2str(fecha_nacimiento.day))).upper()

#aprobaremos el credito solo si gana mas de 25k al mes, o si gana entr 15-25k y tiene <3 dependientes economicos
if 25000 <= usuario["ingreso_men"]:
  usuario["aprobar"] = True
elif (25000 > usuario["ingreso_men"] > 15000) and (usuario["dependientes"] < 3):
  usuario["aprobar"] = True



#credenciales de postgreSQL locales
dbcredentials = {
    "hostname": "localhost", 
    "database": "api_solicitudes_db", 
    "port": 5432,
    "username": "postgres",
    "pwd": "SLBPSgramirez29"
      }
#definiendo la conexion
connection = None
cur = None
try:
    connection = psycopg2.connect(
        host = dbcredentials["hostname"],
        dbname = dbcredentials["database"],
        user = dbcredentials["username"],
        password = dbcredentials["pwd"],
        port = dbcredentials["port"]
    )
    cur = connection.cursor()
    
    #checking if user already in DB
    cur.execute("""SELECT "ID" FROM usuarios_registrados 
        WHERE "RFC" = '"""+usuario["rfc"]+"""' 
        AND "PRIMER_NOMBRE" = '"""+usuario["name"]+"""'
        AND "APELLIDO_PAT" = '"""+usuario["fath_lastname"]+"""'
        AND "APELLIDO_MAT" = '"""+usuario["moth_lastname"]+"""'
        """
    )
    #si el usuario ya se encuentra registrado, se actualizara su registro
    try:
        user_id = cur.fetchall()[0][0]
        #to update the data in the DB
        update_user = """UPDATE usuarios_registrados
        SET "INGRESOS_MENSUALES" = """+str(usuario["ingreso_men"])+""", "DEPENDIENTES" = """ +str(usuario["dependientes"])+""", "APROBADO" = """+str(usuario["aprobar"])+ """
        WHERE "ID" = """+str(user_id)+"""
        """
        cur.execute(update_user)

    except:
        cur.execute('SELECT "ID" FROM usuarios_registrados ORDER BY "ID" DESC LIMIT 1')
        if len(cur.fetchall()) > 0:
            cur.execute('SELECT "ID" FROM usuarios_registrados ORDER BY "ID" DESC LIMIT 1') #repetimos porque al hacer uso del fetchall, se vacia el cursor
            user_id = cur.fetchall()[0][0] + 1 #adding one so that user is not dup
        else:
            user_id = 0
        #to insert the data to the DB
        insert_user = 'INSERT INTO usuarios_registrados ("ID", "PRIMER_NOMBRE", "APELLIDO_PAT", "APELLIDO_MAT", "FECHA_NAC", "RFC", "INGRESOS_MENSUALES", "DEPENDIENTES", "APROBADO") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        user_list=list(usuario.values())
        user_list.insert(0,user_id)
        user_values = user_list
        cur.execute(insert_user, user_values)
    
    connection.commit()
except Exception as error:
    print(error)
finally:
    if cur:
        #se va a mostrar toda la base de datos
        cur.execute("""SELECT "ID", "RFC", "APROBADO"
        FROM usuarios_registrados
        ORDER BY "ID" ASC 
        """
        )
        db_response = cur.fetchall()
        for item in db_response:
            db_columns = dict(zip(["ID", "RFC", "Resp_Solicitud"], item))
            print(db_columns)
        cur.close()
    if connection:
        connection.close()

#respuesta de la API despues de ingrear al usuario en la DB
aprobar = lambda x: "Aprobada" if x else "Rechazada"
print(db_response)
app = Flask(__name__)
@app.route('/')
def respuesta():
    respuesta_dict = {"ID":user_id, "RFC": usuario["rfc"], "RespuestaSolicitud":aprobar(usuario["aprobar"])}
    return jsonify({"Solicitud":db_response})
app.run()