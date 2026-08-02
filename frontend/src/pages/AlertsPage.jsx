import { useState, useEffect, useCallback } from "react";
import { getProcesses, getModelsByProcess, getAlertsByModel, confirmAlert } from "../api";
import useAsync from "../hooks/useAsync";
import Card from "../components/Card";
import Button from "../components/Button";
import Select from "../components/Select";
import Badge from "../components/Badge";
import EmptyState from "../components/EmptyState";

export default function AlertsPage() {
  const [processes, setProcesses] = useState([]);
  const [models, setModels] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [selectedProcess, setSelectedProcess] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [confirmingId, setConfirmingId] = useState(null);

  const { execute: loadProcesses } = useAsync(getProcesses);
  const { execute: loadModels } = useAsync(getModelsByProcess);
  const { execute: loadAlerts } = useAsync(getAlertsByModel);
  const { execute: runConfirm } = useAsync(confirmAlert);

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
      setAlerts([]);
      setSelectedModel("");
      async function load() {
        const m = await loadModels(selectedProcess);
        if (m) setModels(m.filter((m) => m.state === "trained"));
      }
      load();
    }
  }, [selectedProcess]);

  const loadAlertsForModel = useCallback(
    async (modelId) => {
      const a = await loadAlerts(modelId);
      if (a) setAlerts(a);
    },
    [loadAlerts]
  );

  useEffect(() => {
    if (selectedModel) {
      setAlerts([]);
      loadAlertsForModel(selectedModel);
    }
  }, [selectedModel]);

  async function handleConfirm(alertId) {
    setConfirmingId(alertId);
    await runConfirm(alertId);
    setConfirmingId(null);
    loadAlertsForModel(selectedModel);
  }

  const processOptions = processes
    .filter((p) => p.state === "active")
    .map((p) => ({ value: p.id, label: p.name }));

  const modelOptions = models.map((m) => ({
    value: m.id,
    label: `${m.name} (${m.parameters?.n_clusters ?? "?"} clusters)`,
  }));

  const pendingCount = alerts.filter((a) => !a.confirmed).length;
  const confirmedCount = alerts.filter((a) => a.confirmed).length;

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800">Alertas</h1>

      <Card title="Filtros">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        </div>
      </Card>

      {selectedModel && alerts.length > 0 && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-col gap-1">
            <span className="text-xs text-gray-400">Total alertas</span>
            <span className="text-2xl font-bold text-gray-800">
              {alerts.length}
            </span>
          </div>
          <div className="bg-white border border-red-200 rounded-xl p-4 flex flex-col gap-1">
            <span className="text-xs text-gray-400">Pendientes</span>
            <span className="text-2xl font-bold text-red-600">
              {pendingCount}
            </span>
          </div>
          <div className="bg-white border border-green-200 rounded-xl p-4 flex flex-col gap-1">
            <span className="text-xs text-gray-400">Confirmadas</span>
            <span className="text-2xl font-bold text-green-600">
              {confirmedCount}
            </span>
          </div>
        </div>
      )}

      {selectedModel && (
        <Card title="Listado de alertas">
          {alerts.length === 0 ? (
            <EmptyState message="No hay alertas para este modelo" />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-100">
                    <th className="pb-3 font-medium">Fecha</th>
                    <th className="pb-3 font-medium">Cluster</th>
                    <th className="pb-3 font-medium">T² calculado</th>
                    <th className="pb-3 font-medium">Límite</th>
                    <th className="pb-3 font-medium">Estado</th>
                    <th className="pb-3 font-medium">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {alerts.map((a) => (
                    <tr
                      key={a.id}
                      className={`transition ${
                        !a.confirmed ? "bg-red-50 hover:bg-red-100" : "hover:bg-gray-50"
                      }`}
                    >
                      <td className="py-3 text-gray-600">
                        {new Date(a.detection_date).toLocaleString()}
                      </td>
                      <td className="py-3 text-gray-800">
                        Cluster {a.cluster_id}
                      </td>
                      <td className="py-3 font-mono text-red-600 font-medium">
                        {a.t2_statistic.toFixed(4)}
                      </td>
                      <td className="py-3 font-mono text-gray-600">
                        {a.control_limit.toFixed(4)}
                      </td>
                      <td className="py-3">
                        <Badge
                          label={a.confirmed ? "Confirmada" : "Pendiente"}
                          variant={a.confirmed ? "green" : "red"}
                        />
                      </td>
                      <td className="py-3">
                        {!a.confirmed && (
                          <Button
                            variant="secondary"
                            size="sm"
                            disabled={confirmingId === a.id}
                            onClick={() => handleConfirm(a.id)}
                          >
                            {confirmingId === a.id
                              ? "Confirmando..."
                              : "Confirmar"}
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}

      {!selectedModel && (
        <EmptyState message="Selecciona un proceso y un modelo para ver las alertas" />
      )}
    </div>
  );
}