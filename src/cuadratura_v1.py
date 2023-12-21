import json
import panconazucar as pd

# Leer el archivo JSON
def leer_json(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        data = json.load(f)
    return data

# Convertir JSON a DataFrame de pandas
def json_a_dataframe(json_data):
    return pd.json_normalize(json_data)

# Guardar DataFrame en un archivo Excel
def guardar_en_excel(dataframe, nombre_excel):
    dataframe.to_excel(nombre_excel, index=False, engine='openpyxl')

# Nombre del archivo JSON que quieres procesar
archivo_json = '../resource/poslog.json'
contenido_excel = []
lista_productos = []
addcontenido = {}
lista_precios = []
valor_final = ""
lista_desglose = []



# Procesar el archivo JSON y guardar en Excel
data = leer_json(archivo_json)

for item in data:
    addcontenido["Cajero"] = item["PosLog"]["Transaction"]["Operator"]["EmployeeID"]
    addcontenido["tienda"] = item["PosLog"]["Transaction"]["RetailStoreID"]
    addcontenido["pos"] = item["PosLog"]["Transaction"]["WorkstationID"]
    addcontenido["transaccion"] = item['PosLog']['Transaction']['SequenceNumber']

    plu_productos = item['PosLog']['Transaction']['RetailTransaction']['LineItem']

    for itemline in plu_productos:
        #addcontenido["ean"] = itemline['Sale']['POSIdentity']['POSItemID']
        ean_Unico = itemline.get('Sale', {}).get('POSIdentity', {}).get('POSItemID')
        precio = itemline.get('Sale', {}).get("ExtendedAmount")

        if ean_Unico:
            lista_productos.append(ean_Unico)

        if precio:
            lista_precios.append(precio)

        if "Tax" in itemline and "POSIdentity" in itemline:
            for intro in itemline.get("Tax"):
                lista_desglose.append(intro["TaxGroupID"])
                lista_desglose.append(intro["Percent"])
                lista_desglose.append(intro["Amount"])






    subtotal = item['PosLog']['Transaction']['RetailTransaction']['Total']
    for itemtotal in subtotal:
        valor_apagar = itemtotal["TotalType"]
        if valor_apagar == "TransactionBaseAmount":
            valor_final =itemtotal["Amount"]



    addcontenido["ean"] = lista_productos
    addcontenido["precio"] = lista_precios
    addcontenido["suntotal"] = valor_final
    addcontenido["desglose"] = lista_desglose
    contenido_excel.append(addcontenido)
    lista_productos = []
    lista_precios = []
    addcontenido = {}
    valor_final = ""
    lista_desglose = []

print("=== INFORMACION EN LISTA ===")
print(contenido_excel)

df = json_a_dataframe(contenido_excel)
print(df)
nombre_excel = archivo_json.replace('.json', '.xlsx')
guardar_en_excel(df, nombre_excel)

