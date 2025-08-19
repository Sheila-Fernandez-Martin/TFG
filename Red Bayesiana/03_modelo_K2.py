# Cargamos los paquetes necesarios
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pgmpy.estimators import HillClimbSearch
from pgmpy.models import BayesianNetwork as DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
from sklearn.model_selection import train_test_split
import pickle

# MODELO K2  
# Con max_indegree=4 da una precisión de 74%

# -------------------------
# PREPARACIÓN DE LOS DATOS
# -------------------------

# A, 15
# B, 9
# C, 14

letter, max_indregree_letter = 'B', 9  # Cambiar según la letra
# Cargamos los datos
df = pd.read_csv(f'Red Bayesiana\\Data\\data_{letter}.csv', sep=',', index_col=0)

# Eliminamos la ultima columna que no contiene información relevante
df = df.drop(columns=['DAY'])
# Eliminamos las filas que tienen un valor 0 en la columna 'Activity'
df = df[df['Activity'] != 0]

# --------
# MODELO
# --------

# Aprender la estructura de la red bayesiana
hc = HillClimbSearch(df)
model = hc.estimate(scoring_method='k2score', epsilon=1e-13, max_iter=1e6, max_indegree=max_indregree_letter)

# Visualización de la estructura aprendida
G = nx.DiGraph(model.edges())
plt.figure(figsize=(10, 8))
nx.draw(G, with_labels=True, node_color="#00FAC0", edge_color='gray', node_size=2000, font_size=12)
plt.title("Estructura aprendida (DAG)")
plt.show()

# Ajustar el modelo a los datos
bn = DiscreteBayesianNetwork(model.edges())
bn.fit(df, estimator=MaximumLikelihoodEstimator)

# Guardar modelo entrenado
with open(f"modelo_k2_{letter}.pkl", "wb") as f:
    pickle.dump(bn, f)

