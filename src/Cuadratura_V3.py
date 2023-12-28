# Llamado de las liberias en uso
import json
import pandas as pd

# Variables globales
lista_encabezado = []
listado_productos = []
listado_totales = []
listado_medios = []
lista_dataframe = []
lista_factura = []


# Leer el archivo JSON
def leer_json(archivo):
    with open(archivo, "r") as file:
        data = json.load(file)
    return data


# Convertir JSON a DataFrame de pandas
# def json_a_dataframe(json_data):
#     return pd.json_normalize(json_data)


# Unir todos los frames en uno solo para insertar
def concatenar_frames(*args):
    # Concatenar el DataFrame existente con el nuevo y reiniciar el índice
    return pd.concat([i for i in args], axis=1)


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
        # Guardar en el archivo Excel
        dataframe.to_excel(nombre_excel, index=False, engine='openpyxl', **excel_params)
        print("Datos guardados exitosamente en el archivo Excel.")
    except FileNotFoundError:
        # Si el archivo no existe, guardar el DataFrame directamente
        dataframe.to_excel(nombre_excel, index=False, engine='openpyxl', **excel_params)
        print("Archivo Excel creado y datos guardados exitosamente.")


# def eliminar_ean_repetidos(listado):
#     # Crear un diccionario para realizar el seguimiento de los montos acumulados
#     montos_acumulados = {}
#
#     # Iterar sobre la lista original y actualizar los montos acumulados
#     for diccionario in listado:
#         ean = diccionario['ean']
#         precio = float(diccionario['precio'])
#
#         if ean in montos_acumulados:
#             montos_acumulados[ean] += precio
#         else:
#             montos_acumulados[ean] = precio
#
#         # Crear una nueva lista de diccionarios con los montos acumulados
#         nueva_lista_diccionarios = [{'ean': ean, 'precio_acumulado': str(monto)} for ean, monto in
#                                     montos_acumulados.items()]
#
#     return nueva_lista_diccionarios


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


    # guardar_en_excel(df, archivo_excel, hoja='Hoja1', columna_inicio=0)


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
                    bases["base"] = float(intro["BaseAmount"])
                    bases["iva"] = intro["TaxGroupID"]
                    bases["valoriva"] = float(intro["Amount"])
                else:
                    bases["ipo"] = intro["TaxGroupID"]
                    bases["valoripo"] = float(intro["Amount"])
            listado_productos.append(bases)

    print("==== Finalizacion obtenido datos de las bases ====")


def obtener_totales(data):
    print("=== Obtenido totales de la transacion ===")
    line_total = data["PosLog"]["Transaction"]["RetailTransaction"]["Total"]
    valor_total = {}
    for total in line_total:

        if "TransactionDiscountAmount" in total.values():
            valor_total["Descuento"] = float(total["Amount"])

        if "TransactionBaseAmount" in total.values():
            valor_total["Subtotal"] = float(total["Amount"])
            listado_totales.append(valor_total)


    print("==== Finalizacion obtenido totales de la transacion ====")


def obtener_medio_pago(data):
    print("=== Obtenido la informacion del medio de pago")
    line_item = data["PosLog"]["Transaction"]["RetailTransaction"]["LineItem"]
    for item_interno in line_item:
        medios = {}
        if "Tender" in item_interno:
            print(item_interno)
            """if item_interno["Tender"]["TenderID"]:
                medios["Tipo_medio"] = item_interno["Tender"]["TenderID"]
                medios["Medio_monto"] = item_interno["Tender"]["Amount"]"""
            if "Rounding" in item_interno["Tender"]:
                medios["Redondeo"] = float(item_interno["Tender"]["Rounding"])
            else:
                medios["Redondeo"] = None

            if "Donation" in item_interno["Tender"]:
                medios["Donacion"] = float(item_interno["Tender"]["Donation"])

            else:
                medios["Donacion"] = None

            listado_medios.append(medios)

    print("==== Finalizacion obtenido la informacion del medio de pago ====")

def obtener_infor_facturacion(data):
    factura = {}
    try:
        customer = data["PosLog"]["Transaction"]["RetailTransaction"]["Customer"]
        if customer["CustomerID"] == "222222222222":
            factura["Factura"] = 3
        else:
            factura["Factura"] = 2

    except KeyError:
        factura["Factura"] = 1

    lista_factura.append(factura)



# Recorido de los json
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
    obtener_infor_facturacion(item)
    frame_encabezado = pd.DataFrame(lista_encabezado)
    frame_productos = pd.DataFrame(listado_productos)
    frame_totales = pd.DataFrame(listado_totales)
    frame_medios = pd.DataFrame(listado_medios)
    frame_factura = pd.DataFrame(lista_factura)
    dataframe_completo = concatenar_frames(frame_encabezado, frame_productos, frame_totales, frame_medios, frame_factura)
    lista_encabezado = []
    listado_productos = []
    listado_totales = []
    listado_medios = []
    lista_factura = []
    lista_dataframe.append(dataframe_completo.copy())
    # dataframe_completo = None
    # dataframe_completo = pd.DataFrame()
# print(lista_dataframe)

dataframe_final = pd.concat(lista_dataframe)
print(dataframe_final)

# Guardar informacion en el excel
guardar_en_excel(dataframe_final, archivo_excel, hoja='Hoja1', columna_inicio=0)
