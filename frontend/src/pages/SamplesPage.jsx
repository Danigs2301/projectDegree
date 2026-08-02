import { useState, useEffect, useCallback } from "react";
import {
  getProcesses,
  getSamplesByProcess,
  createSample,
  deleteSample,
  getVariables,
} from "../api";
import useAsync from "../hooks/useAsync";
import Card from "../components/Card";
import Button from "../components/Button";
import Select from "../components/Select";
import Input from "../components/Input";
import EmptyState from "../components/EmptyState";

export default function SamplesPage() {
  const [processes, setProcesses] = useState([]);
  const [variables, setVariables] = useState([]);
  const [samples, setSamples] = useState([]);
  const [selectedProcess, setSelectedProcess] = useState("");
  const [measurements, setMeasurements] = useState({});

  const { execute: loadProcesses } = useAsync(getProcesses);
  const { execute: loadVariables } = useAsync(getVariables);
  const { execute: loadSamples } = useAsync(getSamplesByProcess);
  const { execute: runCreate, loading: creating } = useAsync(createSample);
  const { execute: runDelete } = useAsync(deleteSample);

  useEffect(() => {
    async function init() {
      const [p, v] = await Promise.all([loadProcesses(), loadVariables()]);
      if (p) setProcesses(p);
      if (v) setVariables(v);
    }
    init();
  }, []);

  const loadSamplesForProcess = useCallback(
    async (processId) => {
      const s = await loadSamples(processId);
      if (s) setSamples(s);
    },
    [loadSamples]
  );

  useEffect(() => {
    if (selectedProcess) {
      setSamples([]);
      setMeasurements({});
      loadSamplesForProcess(selectedProcess);
    }
  }, [selectedProcess]);

  const currentProcess = processes.find((p) => p.id === selectedProcess);
  const processVariables = currentProcess
    ? variables.filter((v) => currentProcess.variable_ids.includes(v.id))
    : [];

  function handleMeasurementChange(variableId, value) {
    setMeasurements((prev) => ({ ...prev, [variableId]: value }));
  }
  const [lastDetection, setLastDetection] = useState(null);

    async function handleCreate() {
    if (!selectedProcess) return;
    const measurementList = processVariables.map((v) => ({
        variable_id: v.id,
        value: parseFloat(measurements[v.id] || 0),
    }));

    const result = await runCreate({
        process_id: selectedProcess,
        measurements: measurementList,
    });

    if (result) {
        setMeasurements({});
        setLastDetection(result.detection);
        loadSamplesForProcess(selectedProcess);
    }
    }

  const processOptions = processes
    .filter((p) => p.state === "active")
    .map((p) => ({ value: p.id, label: p.name }));

  const canCreate =
    selectedProcess &&
    processVariables.length > 0 &&
    processVariables.every(
      (v) => measurements[v.id] !== undefined && measurements[v.id] !== ""
    );

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800">Muestras</h1>

      <Card title="Seleccionar proceso">
        <Select
          label="Proceso"
          options={processOptions}
          value={selectedProcess}
          onChange={(e) => setSelectedProcess(e.target.value)}
        />
      </Card>

      {selectedProcess && processVariables.length > 0 && (
        <Card title="Nueva muestra">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
            {processVariables.map((v) => (
              <Input
                key={v.id}
                label={`${v.name} (${v.unit})`}
                type="number"
                placeholder="0.0"
                value={measurements[v.id] || ""}
                onChange={(e) =>
                  handleMeasurementChange(v.id, e.target.value)
                }
              />
            ))}
          </div>
          <Button onClick={handleCreate} disabled={creating || !canCreate}>
            {creating ? "Registrando..." : "Registrar muestra"}
          </Button>
          {lastDetection && (
            <div className={`mt-4 rounded-lg p-3 border text-sm ${
                lastDetection.is_anomaly
                ? "bg-red-50 border-red-200 text-red-700"
                : "bg-green-50 border-green-200 text-green-700"
            }`}>
                <div className="flex items-center gap-2 font-medium mb-1">
                <span>{lastDetection.is_anomaly ? "⚠️ Anomalía detectada" : "✅ Muestra bajo control"}</span>
                </div>
                <div className="text-xs flex gap-4">
                <span>T²: <strong>{lastDetection.t2_statistic}</strong></span>
                <span>Límite: <strong>{lastDetection.control_limit}</strong></span>
                <span>Cluster: <strong>{lastDetection.cluster_id}</strong></span>
                </div>
            </div>
        )}
        </Card>
      )}

      {selectedProcess && (
        <Card title="Muestras registradas">
          {samples.length === 0 ? (
            <EmptyState message="No hay muestras para este proceso" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-100">
                    <th className="pb-3 font-medium">Fecha</th>
                    {processVariables.map((v) => (
                      <th key={v.id} className="pb-3 font-medium">
                        {v.name} ({v.unit})
                      </th>
                    ))}
                    <th className="pb-3 font-medium">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {samples.map((s) => (
                    <tr key={s.id} className="hover:bg-gray-50 transition">
                      <td className="py-3 text-gray-600">
                        {new Date(s.date).toLocaleString()}
                      </td>
                      {processVariables.map((v) => {
                        const m = s.measurements.find(
                          (m) => m.variable_id === v.id
                        );
                        return (
                          <td key={v.id} className="py-3 text-gray-800">
                            {m ? m.value : "-"}
                          </td>
                        );
                      })}
                      <td className="py-3">
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={async () => {
                            await runDelete(s.id);
                            loadSamplesForProcess(selectedProcess);
                          }}
                        >
                          Eliminar
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}