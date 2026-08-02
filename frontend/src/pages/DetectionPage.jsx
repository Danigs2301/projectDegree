import { useState, useEffect } from "react";
import {
  getProcesses,
  getModelsByProcess,
  getSamplesByProcess,
  detect,
} from "../api";
import useAsync from "../hooks/useAsync";
import Card from "../components/Card";
import Button from "../components/Button";
import Select from "../components/Select";
import Badge from "../components/Badge";
import EmptyState from "../components/EmptyState";

export default function DetectionPage() {
  const [processes, setProcesses] = useState([]);
  const [models, setModels] = useState([]);
  const [samples, setSamples] = useState([]);
  const [selectedProcess, setSelectedProcess] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [selectedSample, setSelectedSample] = useState("");
  const [result, setResult] = useState(null);

  const { execute: loadProcesses } = useAsync(getProcesses);
  const { execute: loadModels } = useAsync(getModelsByProcess);
  const { execute: loadSamples } = useAsync(getSamplesByProcess);
  const { execute: runDetect, loading: detecting } = useAsync(detect);

  useEffect(() => {
    async function init() {
      const p = await loadProcesses();
      if (p) setProcesses(p);
    }
    init();
  }, []);

  useEffect(() => {
    if (selectedProcess) {
      setModels([]);
      setSamples([]);
      setSelectedModel("");
      setSelectedSample("");
      setResult(null);

      async function load() {
        const [m, s] = await Promise.all([
          loadModels(selectedProcess),
          loadSamples(selectedProcess),
        ]);
        if (m) setModels(m.filter((m) => m.state === "trained"));
        if (s) setSamples(s);
      }
      load();
    }
  }, [selectedProcess]);

  async function handleDetect() {
    if (!selectedModel || !selectedSample) return;
    setResult(null);
    const r = await runDetect({
      model_id: selectedModel,
      sample_id: selectedSample,
    });
    if (r) setResult(r);
  }

  const processOptions = processes
    .filter((p) => p.state === "active")
    .map((p) => ({ value: p.id, label: p.name }));

  const modelOptions = models.map((m) => ({
    value: m.id,
    label: `${m.name} (${m.parameters?.n_clusters ?? "?"} clusters)`,
  }));

  const sampleOptions = samples.map((s) => ({
    value: s.id,
    label: `Muestra ${new Date(s.date).toLocaleString()}`,
  }));

  const canDetect = selectedModel && selectedSample;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800">Detección de Cambios</h1>

      <Card title="Configuración">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <Select
            label="Proceso"
            options={processOptions}
            value={selectedProcess}
            onChange={(e) => setSelectedProcess(e.target.value)}
          />
          <Select
            label="Modelo"
            options={modelOptions}
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={!selectedProcess || models.length === 0}
          />
          <Select
            label="Muestra"
            options={sampleOptions}
            value={selectedSample}
            onChange={(e) => setSelectedSample(e.target.value)}
            disabled={!selectedProcess || samples.length === 0}
          />
        </div>

        {selectedProcess && models.length === 0 && (
          <p className="text-sm text-yellow-600 mb-4">
            No hay modelos entrenados para este proceso.
          </p>
        )}

        <Button
          onClick={handleDetect}
          disabled={detecting || !canDetect}
          size="lg"
        >
          {detecting ? "Analizando..." : "Ejecutar detección"}
        </Button>
      </Card>

      {result && (
        <Card title="Resultado">
          <div
            className={`rounded-lg p-4 mb-6 border ${
              result.is_anomaly
                ? "bg-red-50 border-red-200"
                : "bg-green-50 border-green-200"
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">
                {result.is_anomaly ? "⚠️" : "✅"}
              </span>
              <div>
                <p
                  className={`font-semibold text-lg ${
                    result.is_anomaly ? "text-red-700" : "text-green-700"
                  }`}
                >
                  {result.is_anomaly
                    ? "Cambio de proceso detectado"
                    : "Proceso bajo control"}
                </p>
                <p className="text-sm text-gray-500">
                  {result.is_anomaly
                    ? "El estadístico T² superó el límite de control. Se generó una alerta."
                    : "El estadístico T² está dentro del límite de control."}
                </p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex flex-col gap-1 bg-gray-50 rounded-lg p-3">
              <span className="text-xs text-gray-400">Cluster asignado</span>
              <span className="text-sm font-semibold text-gray-800">
                Cluster {result.cluster_id}
              </span>
            </div>
            <div className="flex flex-col gap-1 bg-gray-50 rounded-lg p-3">
              <span className="text-xs text-gray-400">T² calculado</span>
              <span
                className={`text-sm font-semibold ${
                  result.is_anomaly ? "text-red-600" : "text-gray-800"
                }`}
              >
                {result.t2_statistic.toFixed(4)}
              </span>
            </div>
            <div className="flex flex-col gap-1 bg-gray-50 rounded-lg p-3">
              <span className="text-xs text-gray-400">Límite de control</span>
              <span className="text-sm font-semibold text-gray-800">
                {result.control_limit.toFixed(4)}
              </span>
            </div>
            <div className="flex flex-col gap-1 bg-gray-50 rounded-lg p-3">
              <span className="text-xs text-gray-400">Estado</span>
              <Badge
                label={result.is_anomaly ? "Anomalía" : "Normal"}
                variant={result.is_anomaly ? "red" : "green"}
              />
            </div>
          </div>

          {result.alert_id && (
            <div className="mt-4 text-sm text-gray-500">
              Alerta generada:{" "}
              <span className="font-mono text-gray-700">{result.alert_id}</span>
            </div>
          )}
        </Card>
      )}

      {result === null && selectedProcess && canDetect && (
        <EmptyState message="Ejecuta la detección para ver el resultado" />
      )}
    </div>
  );
}