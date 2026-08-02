import { useState, useEffect, useCallback } from "react";
import { getVariables, createVariable, deleteVariable } from "../api";
import useAsync from "../hooks/useAsync";
import Card from "../components/Card";
import Button from "../components/Button";
import Input from "../components/Input";
import Badge from "../components/Badge";
import EmptyState from "../components/EmptyState";

export default function VariablesPage() {
  const [variables, setVariables] = useState([]);
  const [name, setName] = useState("");
  const [unit, setUnit] = useState("");

  const { execute: loadVariables } = useAsync(getVariables);
  const { execute: runCreate, loading: creating } = useAsync(createVariable);
  const { execute: runDelete } = useAsync(deleteVariable);

  const load = useCallback(async () => {
    const v = await loadVariables();
    if (v) setVariables(v);
  }, [loadVariables]);

  useEffect(() => { load(); }, [load]);

  async function handleCreate() {
    if (!name.trim() || !unit.trim()) return;
    const v = await runCreate({ name, unit });
    if (v) { setName(""); setUnit(""); load(); }
  }

  async function handleDelete(id) {
    await runDelete(id);
    load();
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800">Variables</h1>

      <Card title="Nueva variable">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <Input
              label="Nombre"
              placeholder="Ej. Temperatura"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="w-36">
            <Input
              label="Unidad"
              placeholder="Ej. °C"
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleCreate()}
            />
          </div>
          <Button
            onClick={handleCreate}
            disabled={creating || !name.trim() || !unit.trim()}
          >
            {creating ? "Creando..." : "Crear"}
          </Button>
        </div>
      </Card>

      <Card title="Variables registradas">
        {variables.length === 0 ? (
          <EmptyState message="No hay variables registradas" />
        ) : (
          <ul className="divide-y divide-gray-100">
            {variables.map((v) => (
              <li
                key={v.id}
                className="flex items-center justify-between py-3"
              >
                <div className="flex items-center gap-3">
                  <span className="text-sm font-medium text-gray-800">
                    {v.name}
                  </span>
                  <Badge label={v.unit} variant="blue" />
                </div>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleDelete(v.id)}
                >
                  Eliminar
                </Button>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}