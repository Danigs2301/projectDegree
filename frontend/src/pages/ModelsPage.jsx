import { useState, useEffect, useCallback } from "react";
import {
  getProcesses,
  getModelsByProcess,
  createModel,
  trainModel,
  deleteModel,
} from "../api";
import useAsync from "../hooks/useAsync";
import Card from "../components/Card";
import Button from "../components/Button";
import Input from "../components/Input";
import Select from "../components/Select";
import Badge from "../components/Badge";
import EmptyState from "../components/EmptyState";

export default function ModelsPage() {
  const [processes, setProcesses] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedProcess, setSelectedProcess] = useState("");
  const [name, setName] = useState("");
  const [trainingId, setTrainingId] = useState(null);

  const { execute: loadProcesses } = useAsync(getProcesses);
  const { execute: loadModels } = useAsync(getModelsByProcess);
  const { execute: runCreate, loading: creating } = useAsync(createModel);
  const { execute: runTrain } = useAsync(trainModel);
  const { execute: runDelete } = useAsync(deleteModel);

  useEffect(() => {
    async function init() {
      const p = await loadProcesses();
      if (p) setProcesses(p);
    }
    init();
  }, []);

  const loadModelsForProcess = useCallback(
    async (processId) => {
      const m = await loadModels(processId);
      if (m) setModels(m);
    },
    [loadModels]
  );

  useEffect(() => {
    if (selectedProcess) {
      setModels([]);
      loadModelsForProcess(selectedProcess);
    }
  }, [selectedProcess]);

  async function handleCreate() {
    if (!name.trim() || !selectedProcess) return;
    const m = await runCreate({
      name,
      type_model: "KMeans-Mahalanobis",
      process_id: selectedProcess,
    });
    if (m) {
      setName("");
      loadModelsForProcess(selectedProcess);
    }
  }

  async function handleTrain(modelId) {
    setTrainingId(modelId);
    await runTrain(modelId);
    setTrainingId(null);
    loadModelsForProcess(selectedProcess);
  }

  async function handleDelete(modelId) {
    await runDelete(modelId);
    loadModelsForProcess(selectedProcess);
  }

  const processOptions = processes
    .filter((p) => p.state === "active")
    .map((p) => ({ value: p.id, label: p.name }));

  function stateVariant(state) {
    switch (state) {
      case "trained": return "green";
      case "inactive": return "gray";
      default: return "yellow";
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800">Modelos</h1>

      <Card title="Seleccionar proceso">
        <Select
          label="Proceso"
          options={processOptions}
          value={selectedProcess}
          onChange={(e) => setSelectedProcess(e.target.value)}
        />
      </Card>

      {selectedProcess && (
        <Card title="Nuevo modelo">
          <div className="flex gap-3 items-end">
            <div className="flex-1">
              <Input
                label="Nombre del modelo"
                placeholder="Ej. Modelo KMeans v1"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCreate()}
              />
            </div>
            <Button
              onClick={handleCreate}
              disabled={creating || !name.trim()}
            >
              {creating ? "Creando..." : "Crear"}
            </Button>
          </div>
        </Card>
      )}

      {selectedProcess && (
        <Card title="Modelos del proceso">
          {models.length === 0 ? (
            <EmptyState message="No hay modelos para este proceso" />
          ) : (
            <ul className="divide-y divide-gray-100">
              {models.map((m) => (
                <li key={m.id} className="py-4 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <div className="flex flex-col gap-1">
                      <span className="text-sm font-medium text-gray-800">
                        {m.name}
                      </span>
                      <span className="text-xs text-gray-400">
                        {m.type_model} · Entrenado:{" "}
                        {new Date(m.training_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        label={m.state}
                        variant={stateVariant(m.state)}
                      />
                    </div>
                  </div>

                  {m.state === "trained" && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 bg-gray-50 rounded-lg p-3">
                      <div className="flex flex-col">
                        <span className="text-xs text-gray-400">Clusters</span>
                        <span className="text-sm font-medium text-gray-800">
                          {m.parameters?.n_clusters ?? "-"}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs text-gray-400">Silhouette</span>
                        <span className="text-sm font-medium text-gray-800">
                          {m.accuracy?.toFixed(4) ?? "-"}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs text-gray-400">Variables</span>
                        <span className="text-sm font-medium text-gray-800">
                          {m.parameters?.variable_ids?.length ?? "-"}
                        </span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-xs text-gray-400">Perfiles</span>
                        <span className="text-sm font-medium text-gray-800">
                          {m.cluster_profiles?.length ?? "-"}
                        </span>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2">
                    {m.state !== "inactive" && (
                      <Button
                        variant="success"
                        size="sm"
                        disabled={trainingId === m.id}
                        onClick={() => handleTrain(m.id)}
                      >
                        {trainingId === m.id ? "Entrenando..." : "Entrenar"}
                      </Button>
                    )}
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(m.id)}
                    >
                      Eliminar
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      )}
    </div>
  );
}