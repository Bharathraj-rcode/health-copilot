const BASE = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request(path, options) {
  let res;
  try {
    res = await fetch(BASE + path, options);
  } catch {
    throw new Error("Cannot reach the server. If it was idle, wait a minute and try again.");
  }
  let data = null;
  try {
    data = await res.json();
  } catch {
    // no JSON body
  }
  if (!res.ok) {
    throw new Error((data && data.error) || "Something went wrong. Please try again.");
  }
  return data;
}

export const uploadFile = (file) => {
  const form = new FormData();
  form.append("file", file);
  return request("/api/documents", { method: "POST", body: form });
};
export const loadSample = (name) => request(`/api/samples/${name}`, { method: "POST" });
export const getDocuments = () => request("/api/documents");
export const getTimeline = () => request("/api/timeline");
export const getPatient = () => request("/api/patient");
export const saveAbha = (abha_id) =>
  request("/api/patient", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ abha_id }),
  });
export const fhirUrl = () => BASE + "/api/fhir";

export async function downloadFile(path, filename) {
  let res;
  try {
    res = await fetch(BASE + path);
  } catch {
    throw new Error("Cannot reach the server. If it was idle, wait a minute and try again.");
  }
  if (!res.ok) throw new Error("Could not download the file. Please try again.");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}