import { useState, useEffect, useCallback } from "react";
import {
  getProcesses,
  createProcess,
  deleteProcess,
  getVariables,
  assignVariable,
} from "../api";
import useAsync from "../hooks/useAsync";
import Card from "../components/Card";
import Button from "../components/Button";
import Input from "../components/Input";
import Select from "../components/Select";
import Badge from "../components/Badge";
import EmptyState from "../components/EmptyState";

export default function ProcessesPage() {
  const [processes, setProcesses] = useState([]);
  const [variables, setVariables] = useState([]);
  const [name, setName] = useState("");
  const [selected, setSelected] = useState(null);
  const [variableId, setVariableId] = useState("");

  const { execute: loadProcesses } = useAsync(getProcesses);
  const { execute: loadVariables } = useAsync(getVariables);
  const { execute: runCreate, loading: creating } = useAsync(createProcess);
  const { execute: runDelete } = useAsync(deleteProcess);
  const { execute: runAssign, loading: assigning } = useAsync(assignVariable);

  const load = useCallback(async () => {
    const [p, v] = await Promise.all([loadProcesses(), loadVariables()]);
    if (p) setProcesses(p);
    if (v) setVariables(v);
  }, [loadProcesses, loadVariables]);

  useEffect(() => { load(); }, [load]);

  async function handleCreate() {
    if (!name.trim()) return;
    const p = await runCreate({ name });
    if (p) { setName(""); load(); }
  }

  async function handleDelete(id) {
    await runDelete(id);
    load();
  }

  async function handleAssign() {
    if (!selected || !variableId) return;
    await runAssign(selected.id, variableId);
    setVariableId("");
    load();
  }

  const variableOptions = variables.map((v) => ({
    value: v.id,
    label: `${v.name} (${v.unit})`,
  }));

  const assignedIds = selected?.variable_ids ?? [];
  const assignedVariables = variables.filter((v) => assignedIds.includes(v.id));
  const availableOptions = variableOptions.filter(
    (o) => !assignedIds.includes(o.value)
  );

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800">Procesos</h1>

      <Card title="Nuevo proceso">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <Input
              label="Nombre"
              placeholder="Ej. Proceso de laminación"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
          </div>
          <Button onClick={handleCreate} disabled={creating || !name.trim()}>
            {creating ? "Creando..." : "Crear"}
          </Button>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card title="Procesos">
          {processes.length === 0 ? (
            <EmptyState message="No hay procesos registrados" />
          ) : (
            <ul className="divide-y divide-gray-100">
              {processes.map((p) => (
                <li
                  key={p.id}
                  className={`flex items-center justify-between py-3 px-2 rounded-lg cursor-pointer transition ${
                    selected?.id === p.id ? "bg-blue-50" : "hover:bg-gray-50"
                  }`}
                  onClick={() => setSelected(p)}
                >
                  <div className="flex flex-col gap-1">
                    <span className="text-sm font-medium text-gray-800">{p.name}</span>
                    <span className="text-xs text-gray-400">
                      {p.variable_ids.length} variable(s)
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      label={p.state}
                      variant={p.state === "active" ? "green" : "gray"}
                    />
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={(e) => { e.stopPropagation(); handleDelete(p.id); }}
                    >
                      Eliminar
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title={selected ? `Variables de: ${selected.name}` : "Variables asignadas"}>
          {!selected ? (
            <EmptyState message="Selecciona un proceso para ver sus variables" />
          ) : (
            <div className="flex flex-col gap-4">
              <div className="flex gap-3 items-end">
                <div className="flex-1">
                  <Select
                    label="Asignar variable"
                    options={availableOptions}
                    value={variableId}
                    onChange={(e) => setVariableId(e.target.value)}
                  />
                </div>
                <Button
                  onClick={handleAssign}
                  disabled={assigning || !variableId}
                >
                  {assigning ? "Asignando..." : "Asignar"}
                </Button>
              </div>

              {assignedVariables.length === 0 ? (
                <EmptyState message="Sin variables asignadas" />
              ) : (
                <ul className="divide-y divide-gray-100">
                  {assignedVariables.map((v) => (
                    <li key={v.id} className="flex items-center justify-between py-2">
                      <span className="text-sm text-gray-700">{v.name}</span>
                      <Badge label={v.unit} variant="blue" />
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}