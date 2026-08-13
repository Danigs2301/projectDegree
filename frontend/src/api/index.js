import { get, post, patch, del } from "./client";

// Processes
export const getProcesses = () => get("/processes/");
export const getProcess = (id) => get(`/processes/${id}`);
export const createProcess = (data) => post("/processes/", data);
export const deleteProcess = (id) => del(`/processes/${id}`);
export const assignVariable = (processId, variableId) =>
  post(`/processes/${processId}/variables`, { variable_id: variableId });

// Variables
export const getVariables = () => get("/variables/");
export const createVariable = (data) => post("/variables/", data);
export const deleteVariable = (id) => del(`/variables/${id}`);

// Samples
export const createSample = (data) => post("/samples/", data);
export const getSamplesByProcess = (processId) =>
  get(`/samples/process/${processId}`);
export const deleteSample = (id) => del(`/samples/${id}`);

// Models
export const getModelsByProcess = (processId) =>
  get(`/models/process/${processId}`);
export const createModel = (data) => post("/models/", data);
export const trainModel = (modelId) => post(`/models/${modelId}/train`);
export const deleteModel = (id) => del(`/models/${id}`);

// Detection
export const detect = (data) => post("/detection/", data);

// Alerts
export const getAlertsByModel = (modelId) => get(`/alerts/model/${modelId}`);
export const confirmAlert = (alertId) => patch(`/alerts/${alertId}/confirm`);

// Summary
export const getAllSummaries = () => get("/summary/");
export const getProcessSummary = (processId, { from, to } = {}) => {
  const params = new URLSearchParams();
  if (from) params.set("from", from);
  if (to) params.set("to", to);
  const query = params.toString();
  return get(`/summary/${processId}${query ? `?${query}` : ""}`);
};