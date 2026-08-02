import { useState, useEffect, useCallback } from "react";
import { getAllSummaries, getProcessSummary, getVariables } from "../api";
import useAsync from "../hooks/useAsync";
import Card from "../components/Card";
import Select from "../components/Select";
import Badge from "../components/Badge";
import EmptyState from "../components/EmptyState";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, BarChart, Bar, Cell,
  ReferenceLine,
} from "recharts";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

function StatCard({ label, value, color = "text-gray-800", sub }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-col gap-1">
      <span className="text-xs text-gray-400">{label}</span>
      <span className={`text-2xl font-bold ${color}`}>{value ?? "—"}</span>
      {sub && <span className="text-xs text-gray-400">{sub}</span>}
    </div>
  );
}

function ControlGauge({ rate }) {
  if (rate === null)
    return <EmptyState message="Sin muestras analizadas aún" />;

  const color =
    rate >= 95 ? "#22c55e" : rate >= 80 ? "#f59e0b" : "#ef4444";
  const label =
    rate >= 95 ? "Proceso estable" : rate >= 80 ? "Atención requerida" : "Proceso inestable";

  return (
    <div className="flex flex-col items-center gap-3 py-4">
      <div
        className="relative flex items-center justify-center rounded-full"
        style={{
          width: 140,
          height: 140,
          background: `conic-gradient(${color} ${rate}%, #e5e7eb ${rate}%)`,
        }}
      >
        <div
          className="absolute bg-white rounded-full flex flex-col items-center justify-center"
          style={{ width: 104, height: 104 }}
        >
          <span className="text-2xl font-bold" style={{ color }}>{rate}%</span>
          <span className="text-xs text-gray-400">bajo control</span>
        </div>
      </div>
      <span className="text-sm font-medium" style={{ color }}>{label}</span>
    </div>
  );
}

const RANGE_OPTIONS = [
  { value: "7", label: "Últimos 7 días" },
  { value: "14", label: "Últimos 14 días" },
  { value: "30", label: "Últimos 30 días" },
  { value: "all", label: "Todo el período" },
];

function AnomalyRateChart({ data }) {
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  if (!data || data.length === 0)
    return <EmptyState message="Sin datos de detección aún" />;

  const filtered =
    startDate || endDate
      ? data.filter((d) => {
          const date = new Date(d.date);
          const from = startDate ? new Date(startDate.setHours(0, 0, 0, 0)) : null;
          const to = endDate ? new Date(endDate.setHours(23, 59, 59, 999)) : null;
          if (from && to) return date >= from && date <= to;
          if (from) return date >= from;
          if (to) return date <= to;
          return true;
        })
      : data;

  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    const d = payload[0]?.payload;
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-3 shadow text-xs">
        <p className="font-medium text-gray-700 mb-1">{label}</p>
        <p className="text-gray-600">Muestras: {d?.total_samples}</p>
        <p className="text-red-500">Anomalías: {d?.anomalies}</p>
        <p className="text-blue-600">Tasa: {d?.rate}%</p>
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Desde:</span>
          <DatePicker
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            maxDate={endDate || new Date()}
            placeholderText="Fecha inicio"
            dateFormat="dd/MM/yyyy"
            isClearable
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-xs outline-none focus:ring-2 focus:ring-blue-500 bg-white w-32"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Hasta:</span>
          <DatePicker
            selected={endDate}
            onChange={(date) => setEndDate(date)}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            maxDate={new Date()}
            placeholderText="Fecha fin"
            dateFormat="dd/MM/yyyy"
            isClearable
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-xs outline-none focus:ring-2 focus:ring-blue-500 bg-white w-32"
          />
        </div>
        {(startDate || endDate) && (
          <button
            className="text-xs text-gray-400 hover:text-gray-600 underline"
            onClick={() => { setStartDate(null); setEndDate(null); }}
          >
            Limpiar
          </button>
        )}
        <span className="text-xs text-gray-400 ml-auto">
          {filtered.length} día(s) mostrado(s)
        </span>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={filtered} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 10 }}
            tickFormatter={(d) => d.slice(5)}
          />
          <YAxis
            tick={{ fontSize: 10 }}
            tickFormatter={(v) => `${v}%`}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="rate" radius={[4, 4, 0, 0]} minPointSize={4}>
            {filtered.map((entry, index) => (
              <Cell
                key={index}
                fill={
                  entry.rate === 0
                    ? "#22c55e"
                    : entry.rate <= 10
                    ? "#f59e0b"
                    : "#ef4444"
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400">
        Verde: 0% · Amarillo: ≤10% · Rojo: &gt;10%
      </p>
    </div>
  );
}

function VariableChart({ data, variableName }) {
  if (!data || data.length === 0)
    return <EmptyState message="Sin muestras registradas" />;

  const values = data.map((d) => d.value);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const std = Math.sqrt(
    values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length
  );
  const ucl = parseFloat((mean + 3 * std).toFixed(4));
  const lcl = parseFloat((mean - 3 * std).toFixed(4));
  const meanFixed = parseFloat(mean.toFixed(4));

  // Submuestreo para no sobrecargar el render
  const MAX_POINTS = 200;
  const step = Math.ceil(data.length / MAX_POINTS);
  const chartData = data
    .filter((_, i) => i % step === 0)
    .map((d, i) => ({ index: i + 1, value: d.value }));

  const outOfControl = chartData.filter(
    (d) => d.value > ucl || d.value < lcl
  ).length;

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs text-gray-600 font-medium">{variableName}</p>
        {outOfControl > 0 && (
          <span className="text-xs text-red-500 font-medium">
            {outOfControl} punto(s) fuera de control
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="index" tick={{ fontSize: 9 }} interval="preserveStartEnd" />
          <YAxis tick={{ fontSize: 9 }} />
          <Tooltip
            formatter={(value, name) => {
              const labels = { value: variableName, ucl: "UCL", lcl: "LCL", mean: "CL" };
              return [typeof value === "number" ? value.toFixed(3) : value, labels[name] ?? name];
            }}
            labelFormatter={(l) => `Muestra ${l}`}
          />
          <ReferenceLine y={ucl} stroke="#ef4444" strokeDasharray="4 3" label={{ value: "UCL", fill: "#ef4444", fontSize: 9, position: "right" }} />
          <ReferenceLine y={meanFixed} stroke="#22c55e" strokeDasharray="4 3" label={{ value: "CL", fill: "#22c55e", fontSize: 9, position: "right" }} />
          <ReferenceLine y={lcl} stroke="#ef4444" strokeDasharray="4 3" label={{ value: "LCL", fill: "#ef4444", fontSize: 9, position: "right" }} />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#8b5cf6"
            strokeWidth={1.5}
            dot={(props) => {
              const { cx, cy, payload } = props;
              const isOut = payload.value > ucl || payload.value < lcl;
              if (!isOut) return <g key={`dot-${payload.index}`} />;
              return (
                <circle
                  key={`dot-${payload.index}`}
                  cx={cx}
                  cy={cy}
                  r={4}
                  fill="#ef4444"
                  stroke="white"
                  strokeWidth={1.5}
                />
              );
            }}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function DashboardPage() {
  const [summaries, setSummaries] = useState([]);
  const [selected, setSelected] = useState(null);
  const [variables, setVariables] = useState([]);

  const { execute: loadSummaries } = useAsync(getAllSummaries);
  const { execute: loadSummary } = useAsync(getProcessSummary);
  const { execute: loadVariables } = useAsync(getVariables);

  useEffect(() => {
    async function init() {
      const [s, v] = await Promise.all([loadSummaries(), loadVariables()]);
      if (s) setSummaries(s);
      if (v) setVariables(v);
    }
    init();
  }, []);

  const handleSelectProcess = useCallback(
    async (processId) => {
      if (!processId) { setSelected(null); return; }
      const s = await loadSummary(processId);
      if (s) setSelected(s);
    },
    [loadSummary]
  );

  const processOptions = summaries.map((s) => ({
    value: s.process_id,
    label: s.process_name,
  }));

  const getVariableName = (varId) => {
    const v = variables.find((v) => v.id === varId);
    return v ? `${v.name} (${v.unit})` : varId;
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

      <Card title="Resumen global">
        {summaries.length === 0 ? (
          <EmptyState message="No hay procesos registrados" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th className="pb-3 font-medium">Proceso</th>
                  <th className="pb-3 font-medium">Estado</th>
                  <th className="pb-3 font-medium">Variables</th>
                  <th className="pb-3 font-medium">Muestras</th>
                  <th className="pb-3 font-medium">Modelos</th>
                  <th className="pb-3 font-medium">Bajo control</th>
                  <th className="pb-3 font-medium">Alertas pendientes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {summaries.map((s) => (
                  <tr
                    key={s.process_id}
                    className="hover:bg-gray-50 transition cursor-pointer"
                    onClick={() => handleSelectProcess(s.process_id)}
                  >
                    <td className="py-3 font-medium text-blue-600">{s.process_name}</td>
                    <td className="py-3">
                      <Badge
                        label={s.state}
                        variant={s.state === "active" ? "green" : "gray"}
                      />
                    </td>
                    <td className="py-3 text-gray-600">{s.n_variables}</td>
                    <td className="py-3 text-gray-600">{s.n_samples}</td>
                    <td className="py-3 text-gray-600">{s.n_trained_models}</td>
                    <td className="py-3">
                      {s.control_rate !== null ? (
                        <span className={`font-semibold ${
                          s.control_rate >= 95 ? "text-green-600"
                          : s.control_rate >= 80 ? "text-yellow-600"
                          : "text-red-600"
                        }`}>
                          {s.control_rate}%
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">Sin análisis</span>
                      )}
                    </td>
                    <td className="py-3">
                      {s.n_pending_alerts > 0 ? (
                        <Badge label={s.n_pending_alerts} variant="red" />
                      ) : (
                        <Badge label="0" variant="green" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Card title="Detalle del proceso">
        <div className="mb-6">
          <Select
            label="Selecciona un proceso"
            options={processOptions}
            value={selected?.process_id ?? ""}
            onChange={(e) => handleSelectProcess(e.target.value)}
          />
        </div>

        {!selected ? (
          <EmptyState message="Selecciona un proceso para ver su detalle" />
        ) : (
          <div className="flex flex-col gap-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Variables" value={selected.n_variables} />
              <StatCard label="Muestras totales" value={selected.n_samples} />
              <StatCard
                label="Muestras analizadas"
                value={selected.total_analyzed}
                sub="pasaron por detección"
              />
              <StatCard
                label="Alertas pendientes"
                value={selected.n_pending_alerts}
                color={selected.n_pending_alerts > 0 ? "text-red-600" : "text-green-600"}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 rounded-xl p-4 flex flex-col">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  Proporción bajo control
                </h3>
                <div className="flex-1 flex items-center justify-center">
                  <ControlGauge rate={selected.control_rate} />
                </div>
              </div>

              <div className="md:col-span-2 bg-gray-50 rounded-xl p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-1">
                  Tasa de anomalías por día
                </h3>
                <AnomalyRateChart data={selected.anomaly_rate_chart} />
              </div>
            </div>

            {Object.keys(selected.variable_charts).length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-4">
                  Gráficas de control por variable
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {Object.entries(selected.variable_charts).map(([varId, data]) => (
                    <div key={varId} className="bg-gray-50 rounded-xl p-4">
                      <VariableChart
                        data={data}
                        variableName={getVariableName(varId)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}