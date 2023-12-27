#Llamado de las liberias en uso
import json
import pandas as pd

#Variables globales
lista_encabezado = []
listado_productos = []
listado_totales = []
listado_medios = []
lista_dataframe = []

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

        lista_dataframe.append(updated_data)
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

def obtener_lista_encabezado(data):
    encabezado = {}
    print("==== Obtenido datos del encabezado ====")
    encabezado["cajero"] = data["PosLog"]["Transaction"]["Operator"]["EmployeeID"]
    encabezado["tienda"] = data["PosLog"]["Transaction"]["RetailStoreID"]
    encabezado["pos"] = data["PosLog"]["Transaction"]["WorkstationID"]
    encabezado["transaccion"] = data["PosLog"]["Transaction"]["SequenceNumber"]
    lista_encabezado.append(encabezado)
    print("==== Finalizacion obtenido datos del encabezado ====")

    # Guardar en el archivo Excel especificando hoja y columna
    df = pd.DataFrame(lista_encabezado)
    guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)

def obtener_informacion_producto(data):
    print("==== Obtenido datos de las bases ====")

    line_item = data["PosLog"]["Transaction"]["RetailTransaction"]["LineItem"]
    for item_interno in line_item:
        bases = {}
        monto = 0
        if "Tax" in item_interno and "POSIdentity" in item_interno:

            for intro in item_interno.get("Tax"):
                ean_Unico = item_interno.get('POSIdentity', {}).get('POSItemID')
                if ean_Unico:
                    bases["ean"] = ean_Unico

                if intro["TaxType"] == 'IVA':
                    bases["base"] = intro["BaseAmount"]
                    bases["iva"] = intro["TaxGroupID"]
                    bases["valoriva"] = intro["Amount"]
                else:
                    bases["ipo"] = intro["TaxGroupID"]
                    bases["valoripo"] = intro["Amount"]
            listado_productos.append(bases)

    df = pd.DataFrame(listado_productos)
    print(listado_productos)
    guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)
    print("==== Finalizacion obtenido datos de las bases ====")

def obtener_totales(data):
    print("=== Obtenido totales de la transacion ===")
    line_total = data["PosLog"]["Transaction"]["RetailTransaction"]["Total"]
    valor_total = {}
    for total in line_total:

        if "TransactionDiscountAmount" in total.values():
            valor_total["Descuento"] = total["Amount"]

        if "TransactionBaseAmount" in total.values():
            valor_total["Subtotal"] = total["Amount"]
            listado_totales.append(valor_total)



    print(listado_totales)
    df = pd.DataFrame(listado_totales)
    guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)
    print("==== Finalizacion obtenido totales de la transacion ====")

def obtener_medio_pago(data):
    print("=== Obtenido la informacion del medio de pago")
    line_item = data["PosLog"]["Transaction"]["RetailTransaction"]["LineItem"]
    for item_interno in line_item:
        medios = {}
        if "Tender" in item_interno:
            print(item_interno)
            if item_interno["Tender"]["TenderID"]:
                medios["Tipo_medio"] = item_interno["Tender"]["TenderID"]
                medios["Medio_monto"] = item_interno["Tender"]["Amount"]
            if item_interno["Tender"]["Rounding"]:
                medios["Redondeo"] = item_interno["Tender"]["Rounding"]

            listado_medios.append(medios)

            """if item_interno["Tender"]["Donation"]:
                medios["Donacion"] = item_interno["Tender"]["Donation"]
                listado_medios.append(medios)"""

    df = pd.DataFrame(listado_medios)
    guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)
    print("==== Finalizacion obtenido la informacion del medio de pago ====")


#Recorido de los json
print("=== Inicio del recorrido Json ===")
# Nombre del archivo JSON que quieres procesar
archivo_json = '../resource/input_poslog.json'
# Nombre del archivo de salida
archivo_excel = '../resource/output.xlsx'

# Procesar el archivo JSON
data = leer_json(archivo_json)

for item in data:
    obtener_lista_encabezado(item)
    obtener_informacion_producto(item)
    obtener_totales(item)
    obtener_medio_pago(item)

#Guardar informacion en el excel



