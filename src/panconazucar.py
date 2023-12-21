import pandas as pd

# Crear dos DataFrames para la concatenación vertical
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})

# Concatenar verticalmente
result_vertical = pd.concat([df1, df2], ignore_index=True)

# Crear dos DataFrames para la concatenación horizontal
df3 = pd.DataFrame({'C': [9, 10], 'D': [11, 12]})
df4 = pd.DataFrame({'C': [13, 14], 'D': [15, 16]})

# Concatenar horizontalmente
result_horizontal = pd.concat([df3, df4], axis=1)

# Concatenar verticalmente y luego horizontalmente
result_mix = pd.concat([result_vertical, result_horizontal], axis=1)

print("Resultado de la concatenación vertical:")
print(result_vertical)

print("\nResultado de la concatenación horizontal:")
print(result_horizontal)

print("\nResultado de la concatenación vertical y luego horizontal:")
print(result_mix)
