# Cargamos las dependencias
import pandas as pd
from funciones_2 import *
from pathlib import Path
import numpy as np
days = ['2017-11-09', '2017-11-13', '2017-11-21']

i,letter= 0,'C'

# Ruta del GT
gt = pd.read_csv(f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-activity.csv', sep=',')
df_predicciones  = pd.read_csv(f'Predicciones\\Data_predicciones\\{days[i]}\\{days[i]}-{letter}-predicciones.csv', sep=',')
# =========================================================
# Agregación de predicciones a intervalos de 30s y comparación con GT
# =========================================================

# --- Paso 1: obtener el primer TIMESTAMP del GT ---

# Aseguramos que exista una columna TIMESTAMP (si está como índice, lo pasamos a columna)
if "TIMESTAMP" not in gt.columns:
    if str(gt.index.name).lower() == "timestamp":
        gt = gt.reset_index()
    else:
        raise KeyError("No encuentro la columna 'TIMESTAMP' en gt.")

# Parseo robusto a datetime
ts_parsed = pd.to_datetime(gt["TIMESTAMP"], errors="coerce", infer_datetime_format=True)
if ts_parsed.isna().mean() > 0.5:  # si falló mucho, probamos dayfirst=True
    ts_parsed = pd.to_datetime(gt["TIMESTAMP"], errors="coerce", infer_datetime_format=True, dayfirst=True)

gt["TIMESTAMP"] = ts_parsed

# Tomamos el primero (mínimo) ignorando NaT
start_ts = gt["TIMESTAMP"].dropna().min()

print("Primer TIMESTAMP del GT:", start_ts)

gt_valid = gt.dropna(subset=["TIMESTAMP"]).copy()
if gt_valid.empty:
    raise ValueError("GT no contiene TIMESTAMP válidos.")

end_ts = gt_valid["TIMESTAMP"].max()

# Nº de filas del GT (sin contar cabecera; len(df) ya excluye cabecera)
n_rows_gt = len(gt_valid)

# Serie de timestamps: empieza en start_ts y suma 30s (n_rows_gt - 1) veces
timestamps_30s = pd.date_range(start=start_ts, periods=n_rows_gt, freq="30s")

calc_end = timestamps_30s[-1]
if calc_end != end_ts:
    print(f"⚠️ Aviso: el último TIMESTAMP calculado ({calc_end}) no coincide con el del GT ({end_ts}).")

df_30s = pd.DataFrame({
    "TIMESTAMP": timestamps_30s,
    "Activity_1": pd.Series([np.nan] * n_rows_gt, dtype="object"),
    "Activity_2": pd.Series([np.nan] * n_rows_gt, dtype="object"),
})


# --- Paso 3: rellenar Activity_1 y Activity_2 en df_30s con el top-2 de PREDICCION por intervalo de 30s ---

# 1) Asegurar que df_predicciones tiene TIMESTAMP bien parseado y alinear fecha si hiciera falta
dfp = df_predicciones.copy()

# Parseo robusto
dfp["TIMESTAMP"] = pd.to_datetime(dfp["TIMESTAMP"], errors="coerce", infer_datetime_format=True)
if dfp["TIMESTAMP"].isna().any():
    # reintento dayfirst si muchos NaT
    t2 = pd.to_datetime(df_predicciones["TIMESTAMP"], errors="coerce", infer_datetime_format=True, dayfirst=True)
    dfp.loc[dfp["TIMESTAMP"].isna(), "TIMESTAMP"] = t2[dfp["TIMESTAMP"].isna()]

dfp = dfp.dropna(subset=["TIMESTAMP"]).copy()

# Alinear fecha de predicciones a la del GT (usamos start_ts calculado en el paso 1)
pred_date = dfp["TIMESTAMP"].dt.date.mode().iloc[0] if not dfp.empty else None
gt_date   = start_ts.date()
if pred_date is not None and pred_date != gt_date:
    dfp["TIMESTAMP"] = pd.to_datetime(
        dfp["TIMESTAMP"].dt.strftime(f"{gt_date} %H:%M:%S"),
        errors="coerce"
    )

# 2) Limitar predicciones al rango de los bins: [primer_ts, ultimo_ts + 30s)
start_bin = df_30s["TIMESTAMP"].iloc[0]
last_bin  = df_30s["TIMESTAMP"].iloc[-1]
end_bin   = last_bin + pd.Timedelta(seconds=30)

dfp = dfp[(dfp["TIMESTAMP"] >= start_bin) & (dfp["TIMESTAMP"] < end_bin)].copy()

# 3) Asignar a cada fila su bin (floor a 30s anclado en start_bin)
delta_sec = (dfp["TIMESTAMP"] - start_bin).dt.total_seconds().astype("int64")
dfp["__BIN__"] = start_bin + pd.to_timedelta((delta_sec // 30) * 30, unit="s")

# 4) Contar ocurrencias por (bin, PREDICCION) y quedarse con las 2 más frecuentes por bin
counts = (
    dfp.groupby(["__BIN__", "PREDICCION"])
       .size()
       .reset_index(name="count")
       .sort_values(["__BIN__", "count", "PREDICCION"], ascending=[True, False, True])
)

# Rank 1 y 2 dentro de cada bin
counts["rank"] = counts.groupby("__BIN__")["count"].cumcount() + 1
top2 = counts[counts["rank"] <= 2].copy()

# Pasar a columnas Activity_1 / Activity_2
pivot = (
    top2.pivot(index="__BIN__", columns="rank", values="PREDICCION")
        .rename(columns={1: "Activity_1", 2: "Activity_2"})
        .reset_index()
        .rename(columns={"__BIN__": "TIMESTAMP"})
)

# 5) Volcar al df_30s (alineando por TIMESTAMP)
df_30s = df_30s.set_index("TIMESTAMP")
pivot  = pivot.set_index("TIMESTAMP")
df_30s[["Activity_1", "Activity_2"]] = pivot[["Activity_1", "Activity_2"]]
df_30s = df_30s.reset_index()

# --- Paso 3.1: Post-procesado de df_30s según reglas ---
# Asegurar tipo objeto para no tener problemas con NaN/strings
df_30s["Activity_1"] = df_30s["Activity_1"].astype("object")
df_30s["Activity_2"] = df_30s["Activity_2"].astype("object")

# Regla 2: si no hubo ninguna predicción en el intervalo (NaN), usar Idle
df_30s["Activity_1"] = df_30s["Activity_1"].fillna("Idle")

# Regla 1: si Activity_2 es NaN, copiar Activity_1 (ya sea ActXX o Idle)
df_30s["Activity_2"] = df_30s["Activity_2"].fillna(df_30s["Activity_1"])

# 6) (Opcional) informe rápido
n_total  = len(df_30s)
n_empty  = int(df_30s["Activity_1"].isna().sum())
print(df_30s)

out_dir = Path("Predicciones") / "Data_predicciones" /str(days[i])
out_dir.mkdir(parents=True, exist_ok=True)

# ruta final del CSV
out_path = out_dir / f"{days[i]}-{letter}-predicciones_30s.csv"
df_30s.to_csv(out_path, index=False)


# -----------------------
# EVALUACIÓN DEL MODELO
# -----------------------

# 0) Asegurar tiempos y ordenar
gt["TIMESTAMP"] = pd.to_datetime(gt["TIMESTAMP"], errors="coerce")
df_30s["TIMESTAMP"] = pd.to_datetime(df_30s["TIMESTAMP"], errors="coerce")

gt = gt.dropna(subset=["TIMESTAMP"]).sort_values("TIMESTAMP").reset_index(drop=True)
df_30s = df_30s.dropna(subset=["TIMESTAMP"]).sort_values("TIMESTAMP").reset_index(drop=True)

# 1) Normalizador de etiquetas: 0/NaN -> 'Idle', números -> 'ActN', resto se deja igual
def norm_label(v):
    if pd.isna(v):
        return "Idle"
    s = str(v).strip()
    if s == "" or s == "0":
        return "Idle"
    try:
        n = int(float(s))
        return f"Act{n}"
    except Exception:
        return s

# 2) Predicciones: mapea tus dos columnas
pred = df_30s.rename(columns={"TIMESTAMP": "TIMESTAMP"}).copy()
pred["Pred1"] = pred["Activity_1"].apply(norm_label)
pred["Pred2"] = pred["Activity_2"].apply(norm_label)

# 3) Ground truth: toma sus dos columnas
gt_ref = gt.copy()
gt_ref["GT1"] = gt_ref["Activity_1"].apply(norm_label)
gt_ref["GT2"] = gt_ref["Activity_2"].apply(norm_label)

# 4) Unir por TIMESTAMP
comp = pd.merge(
    gt_ref[["TIMESTAMP", "GT1", "GT2"]],
    pred[["TIMESTAMP", "Pred1", "Pred2"]],
    on="TIMESTAMP",
    how="left"
)

# Completar predicciones faltantes con Idle
comp["Pred1"] = comp["Pred1"].fillna("Idle")
comp["Pred2"] = comp["Pred2"].fillna("Idle")

# 5) Acierto si cualquiera coincide
comp["correct"] = (
    (comp["Pred1"] == comp["GT1"]) |
    (comp["Pred1"] == comp["GT2"]) |
    (comp["Pred2"] == comp["GT1"]) |
    (comp["Pred2"] == comp["GT2"])
)

acc = comp["correct"].mean()
print(f"Accuracy 30s (match en cualquiera de las dos): {acc:.2%}")

# (Opcional) primeras discrepancias
errores = comp[~comp["correct"]][["TIMESTAMP", "GT1", "GT2", "Pred1", "Pred2"]]
print("\nPrimeras discrepancias:")
print(errores.head(10))
