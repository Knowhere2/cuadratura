#Llamado de las liberias en uso
import json
import pandas as pd

#Variables globales
encabezado = {}
lista_datos = []
productos = {}
lista_productos = []
bases = {}
listado_bases = []
contenido_excel = {}
final = []


# Leer el archivo JSON
def leer_json(archivo):
    with open(archivo,"r") as file:
        data = json.load(file)
    return data

# Convertir JSON a DataFrame de pandas
def json_a_dataframe(json_data):
    return pd.json_normalize(json_data)

# Guardar DataFrame en un archivo Excel
def guardar_en_excel(dataframe, nombre_excel, hoja=None, columna_inicio=None):
    """
    :param dataframe: El DataFrame que se va a guardar.
    :param nombre_excel: El nombre del archivo Excel.
    :param hoja: El nombre de la hoja en la que se guardarán los datos. Si es None, se utiliza la primera hoja por defecto.
    :param columna_inicio: La columna en la que se iniciará la escritura de los datos. Si es None, se inicia en la primera columna por defecto.
    """
    # Parámetros adicionales para la escritura en Excel
    excel_params = {
        'sheet_name': hoja,
        'startcol': columna_inicio
    }

    try:
        # Intentar cargar el archivo Excel existente
        existing_data = pd.read_excel(nombre_excel, sheet_name=hoja)

        # Concatenar el DataFrame existente con el nuevo y reiniciar el índice
        updated_data = pd.concat([existing_data, dataframe], axis=1)

        # Guardar en el archivo Excel
        updated_data.to_excel(nombre_excel, index=False, engine='openpyxl', **excel_params)
        print("Datos guardados exitosamente en el archivo Excel.")
    except FileNotFoundError:
        # Si el archivo no existe, guardar el DataFrame directamente
        dataframe.to_excel(nombre_excel, index=False, engine='openpyxl', **excel_params)
        print("Archivo Excel creado y datos guardados exitosamente.")


def eliminar_ean_repetidos(listado):
    # Crear un diccionario para realizar el seguimiento de los montos acumulados
    montos_acumulados = {}

    # Iterar sobre la lista original y actualizar los montos acumulados
    for diccionario in listado:
        ean = diccionario['ean']
        precio = float(diccionario['precio'])

        if ean in montos_acumulados:
            montos_acumulados[ean] += precio
        else:
            montos_acumulados[ean] = precio

        # Crear una nueva lista de diccionarios con los montos acumulados
        nueva_lista_diccionarios = [{'ean': ean, 'precio_acumulado': str(monto)} for ean, monto in montos_acumulados.items()]

    return nueva_lista_diccionarios


# Nombre del archivo JSON que quieres procesar
archivo_json = '../resource/input_poslog.json'

# Procesar el archivo JSON
data = leer_json(archivo_json)

#Recorido de los json
print("=== Inicio del recorrido Json ===")
for item_json in data:
    print(item_json)
    encabezado["cajero"] = item_json["PosLog"]["Transaction"]["Operator"]["EmployeeID"]
    encabezado["tienda"] = item_json["PosLog"]["Transaction"]["RetailStoreID"]
    encabezado["pos"] = item_json["PosLog"]["Transaction"]["WorkstationID"]
    encabezado["transaccion"] = item_json["PosLog"]["Transaction"]["SequenceNumber"]

    line_item = item_json["PosLog"]["Transaction"]["RetailTransaction"]["LineItem"]
    print("=== Ciclo de item ===")
    for item_interno in line_item:
        ean_Unico = item_interno.get('POSIdentity', {}).get('POSItemID')
        precio = item_interno.get('Sale', {}).get("ExtendedAmount")

        if ean_Unico and precio:
            productos["ean"] = ean_Unico
            productos["precio"] = precio
            lista_productos.append(productos)
            productos = {}


        if "Tax" in item_interno and "POSIdentity" in item_interno:
            for intro in item_interno.get("Tax"):
                if intro["TaxType"] == 'IVA':
                    bases["base"] = intro["BaseAmount"]
                    bases["iva"] = intro["TaxGroupID"]
                    bases["valoriva"] = intro["Amount"]
                else:
                    bases["ipo"] = intro["TaxGroupID"]
                    bases["valoripo"] = intro["Amount"]

            listado_bases.append(bases)
            bases = {}



lista_datos.append(encabezado)
#lista_productos.append(productos)


print("=== Informacion del dicionario contendio ===")
print(lista_datos)
print(eliminar_ean_repetidos(lista_productos))
print(listado_bases)


# Nombre del archivo de salida
archivo_excel = '../resource/output.xlsx'

# Guardar en el archivo Excel especificando hoja y columna
df = pd.DataFrame(lista_datos)
guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)

df = pd.DataFrame(eliminar_ean_repetidos(lista_productos))
guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)

df = pd.DataFrame(listado_bases)
guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)



