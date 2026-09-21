# -*- coding: utf-8 -*-
# Experimento de deteccion controlada (Tablas 7, 8 y 9 del capitulo de Resultados)
import json
import numpy as np
from datetime import datetime
 
SAMPLES_PATH = 'CSProject.samples.json'
MODELS_PATH = 'CSProject.models.json'
PROCESSES_PATH = 'CSProject.processes.json'
 
RNG_SEED = 42
K_LEVELS_UNIFORM = [0.5, 1.0, 2.0]   # desplazamiento simultaneo en TODAS las variables
K_LEVELS_SINGLE = [1.0, 2.0, 3.0]    # desplazamiento en UNA sola variable (falla localizada)
NOISE_MULTIPLIER = 0.15
NOISE_REPLICAS = 30
 
with open(SAMPLES_PATH) as f: samples = json.load(f)
with open(MODELS_PATH) as f: models = json.load(f)
with open(PROCESSES_PATH) as f: processes = json.load(f)
 
proc_by_id = {p['_id']: p for p in processes}
models_by_id = {m['_id']: m for m in models}
 
def parse(d):
    return datetime.fromisoformat(d['$date'].replace('Z', '+00:00'))
 
def mahalanobis_sq(x, centroid, cov):
    diff = x - centroid
    try:
        inv_cov = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        inv_cov = np.linalg.pinv(cov)
    return float(diff @ inv_cov @ diff)
 
def detect_change(x, cluster_profiles):
    min_d = float('inf'); assigned = None
    for cp in cluster_profiles:
        c = np.array(cp['centroid'])
        d = np.linalg.norm(x - c)
        if d < min_d:
            min_d = d; assigned = cp
    centroid = np.array(assigned['centroid'])
    cov = np.array(assigned['covariance_matrix'])
    t2 = mahalanobis_sq(x, centroid, cov)
    is_anom = t2 > assigned['t2_control_limit']
    return t2, assigned['t2_control_limit'], is_anom
 
def build_matrix_dated(proc_samples, variable_ids):
    rows, dates = [], []
    for s in proc_samples:
        m = {meas['variable_id']: meas['value'] for meas in s['measurements']}
        try:
            row = [float(m[v]) for v in variable_ids]
        except KeyError:
            continue
        rows.append(row)
        dates.append(parse(s['date']))
    return np.array(rows, dtype=float), dates
 
def transform(X, scaler_mean, scaler_scale, pca_components=None, pca_mean=None):
    X_scaled = (X - np.array(scaler_mean)) / np.array(scaler_scale)
    if pca_components is not None:
        comp = np.array(pca_components); pmean = np.array(pca_mean)
        X_pca = (X_scaled - pmean) @ comp.T
        return X_pca
    return X_scaled
 
TARGET_MODELS = {
    'Chemical process': '6a7791cceb901dd076e9427e',
    'Red Wine': '6a7d443cfd7ef0de49ea3eac',
    'White Wine': '6a7d5823fd7ef0de49ea3ead',
}
 
rng = np.random.default_rng(RNG_SEED)
report = {}
 
for proc_name, model_id in TARGET_MODELS.items():
    model = models_by_id[model_id]
    proc_id = model['process_id']
    proc = proc_by_id[proc_id]
    variable_ids = proc['variable_ids']
    proc_samples = [s for s in samples if s['process_id'] == proc_id]
    X_all, dates_all = build_matrix_dated(proc_samples, variable_ids)
    tdate = parse(model['training_date'])
    is_new = np.array([d > tdate for d in dates_all]) if len(dates_all) else np.array([])
    X_new = X_all[is_new]
    n_new = len(X_new)
 
    params = model['parameters']
    scaler_mean = np.array(params['scaler_mean'])
    scaler_scale = np.array(params['scaler_scale'])  # sigma_j de entrenamiento
    pca_components = params.get('pca_components')
    pca_mean = params.get('pca_mean')
    cluster_profiles = model['cluster_profiles']
 
    entry = {
        'n_new_real_samples': n_new,
        'sensitivity_uniform_by_k': {},
        'sensitivity_single_variable_by_k': {},
        'noise_robustness': {},
    }
 
    # --- Sensibilidad A: desplazamiento uniforme (todas las variables a la vez) ---
    for k in K_LEVELS_UNIFORM:
        n_flagged = 0
        for x in X_new:
            x_shifted = x + k * scaler_scale
            x_final = transform(x_shifted[None, :], scaler_mean, scaler_scale,
                                 pca_components, pca_mean)[0]
            _, _, is_anom = detect_change(x_final, cluster_profiles)
            n_flagged += int(is_anom)
        entry['sensitivity_uniform_by_k'][f'{k}sigma'] = {
            'n_tested': n_new, 'n_flagged': n_flagged,
            'tpr_pct': round(100 * n_flagged / n_new, 2) if n_new else None,
        }
 
    # --- Sensibilidad B: desplazamiento en UNA sola variable (falla localizada) ---
    for k in K_LEVELS_SINGLE:
        per_var_tpr = []
        for j, var_id in enumerate(variable_ids):
            n_flagged = 0
            for x in X_new:
                x_shifted = x.copy()
                x_shifted[j] = x_shifted[j] + k * scaler_scale[j]
                x_final = transform(x_shifted[None, :], scaler_mean, scaler_scale,
                                     pca_components, pca_mean)[0]
                _, _, is_anom = detect_change(x_final, cluster_profiles)
                n_flagged += int(is_anom)
            per_var_tpr.append(100 * n_flagged / n_new if n_new else 0.0)
        entry['sensitivity_single_variable_by_k'][f'{k}sigma'] = {
            'n_variables_tested': len(variable_ids),
            'avg_tpr_pct': round(float(np.mean(per_var_tpr)), 2),
            'min_tpr_pct': round(float(np.min(per_var_tpr)), 2),
            'max_tpr_pct': round(float(np.max(per_var_tpr)), 2),
        }
 
    # --- Robustez al ruido: ruido gaussiano sin desplazamiento real ---
    n_noise_total = 0
    n_noise_flagged = 0
    for x in X_new:
        noise = rng.normal(loc=0.0, scale=NOISE_MULTIPLIER * scaler_scale,
                            size=(NOISE_REPLICAS, len(x)))
        X_noisy = x[None, :] + noise
        X_noisy_final = transform(X_noisy, scaler_mean, scaler_scale,
                                   pca_components, pca_mean)
        for x_final in X_noisy_final:
            _, _, is_anom = detect_change(x_final, cluster_profiles)
            n_noise_total += 1
            n_noise_flagged += int(is_anom)
    entry['noise_robustness'] = {
        'noise_multiplier_sigma': NOISE_MULTIPLIER,
        'replicas_per_sample': NOISE_REPLICAS,
        'n_tested': n_noise_total, 'n_false_alarms': n_noise_flagged,
        'false_alarm_rate_pct': round(100 * n_noise_flagged / n_noise_total, 2),
    }
 
    report[proc_name] = entry
 
with open('experiment_results.json', 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
