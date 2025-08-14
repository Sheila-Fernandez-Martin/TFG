# Cargamos los paquetes necesarios
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pgmpy.estimators import HillClimbSearch
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator, ExpectationMaximization
from pgmpy.inference import VariableElimination
from sklearn.model_selection import train_test_split
from pgmpy.estimators import TreeSearch


# MODELO TREESEARCH 
# Da un 66% de precisión

letter = 'A'
df = pd.read_csv(f'Red Bayesiana\\Data\\data_{letter}.csv', sep=',', index_col=0)

# Eliminamos la ultima columna que no contiene información relevante
df = df.drop(columns=['DAY'])
# Eliminamos las filas que tienen un valor 0 en la columna 'Activity'
df = df[df['Activity'] != 0]

# Dividimos ahora trainval en train y validación
df_train, df_val = train_test_split(df, test_size=0.15, random_state=40, stratify=df['Activity'])

# Aprender la estructura de la red bayesiana
ts = TreeSearch(df_train, root_node="Activity")
model = ts.estimate() 

bn = DiscreteBayesianNetwork(model.edges())
bn.fit(df_train, estimator=MaximumLikelihoodEstimator, n_jobs=10)

infer = VariableElimination(bn)


model_vars = list(bn.nodes())  # Variables que el modelo sí conoce
model_vars.remove('Activity')  # Queremos predecir esta
print(model_vars)
correct = 0
predictions = []

for _, row in df_val.iterrows():
    # Filtrar solo columnas que están en el modelo
    evidence = row[model_vars].to_dict()
    prediction = infer.map_query(['Activity'], evidence=evidence)
    predictions.append(prediction['Activity'])
    if prediction['Activity'] == row['Activity']:
        correct += 1

accuracy = correct / len(df_val)
# Calculamos las frecuencias de las predicciones
pred = list(set(predictions))
frecuencias = {p: predictions.count(p) for p in pred}

print(f"\n\033[1;32mPrecisión del modelo: {accuracy:.2f}\033[0m")
print(f"\033[1;34mPredicciones\033[0m:")
for pred in frecuencias:
    print(f"{pred}: {frecuencias[pred]} veces")

# model es un objeto pgmpy.base.DAG
G = nx.DiGraph(model.edges())

plt.figure(figsize=(10, 8))
nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray', node_size=2000, font_size=12)
plt.title("Estructura aprendida (DAG)")
plt.show()