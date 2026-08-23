"use client";

import { useState } from "react";

type Resolution = {
  incident_id: string;
  incident_type: string;
  root_cause: string;
  recommended_action: string;
  target_system: string;
  confidence_score?: number;
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [resolution, setResolution] = useState<Resolution | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeLog() {
    if (!file) {
      setError("Please select a log file.");
      return;
    }

    setLoading(true);
    setError("");
    setResolution(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        "http://localhost:8000/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Backend returned an error.");
      }

      const data = await response.json();

      setResolution(data.resolution);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect to FastAPI."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-6xl px-6 py-12">

        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-blue-400">
            ENTERPRISE AI OPERATIONS
          </p>

          <h1 className="text-4xl font-bold">
            Multi-Agent Incident Resolution
          </h1>

          <p className="mt-3 text-slate-400">
            Upload an HDFS log and allow the agent pipeline
            to detect, diagnose and resolve the incident.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-7">

          <h2 className="mb-5 text-xl font-semibold">
            Log Analysis
          </h2>

          <input
            type="file"
            accept=".log,.txt"
            onChange={(e) =>
              setFile(e.target.files?.[0] ?? null)
            }
            className="block w-full rounded-lg border
                       border-slate-700 bg-slate-950 p-3"
          />

          {file && (
            <p className="mt-3 text-sm text-slate-400">
              Selected: {file.name}
            </p>
          )}

          <button
            onClick={analyzeLog}
            disabled={loading}
            className="mt-5 rounded-lg bg-blue-600
                       px-6 py-3 font-semibold
                       hover:bg-blue-500
                       disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Analyze Incident"}
          </button>

          {error && (
            <div className="mt-5 rounded-lg bg-red-950 p-4 text-red-300">
              {error}
            </div>
          )}
        </div>

        {resolution && (
          <div className="mt-8">

            <div className="mb-5 flex items-center justify-between">
              <h2 className="text-2xl font-bold">
                Incident Detected
              </h2>

              <span className="rounded-full bg-red-950 px-4 py-2 text-sm text-red-300">
                DETECTED
              </span>
            </div>

            <div className="grid gap-5 md:grid-cols-3">

              <Card
                title="Incident"
                value={resolution.incident_type}
              />

              <Card
                title="Target"
                value={resolution.target_system}
              />

              <Card
                title="Confidence"
                value={
                  resolution.confidence_score !== undefined
                    ? `${Math.round(
                        resolution.confidence_score * 100
                      )}%`
                    : "N/A"
                }
              />

            </div>

            <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-900 p-7">

              <h3 className="text-lg font-semibold">
                Agent Diagnosis
              </h3>

              <div className="mt-6 space-y-5">

                <Info
                  label="Incident ID"
                  value={resolution.incident_id}
                />

                <Info
                  label="Root Cause"
                  value={resolution.root_cause}
                />

                <Info
                  label="Recommended Action"
                  value={resolution.recommended_action}
                />

                <Info
                  label="Target System"
                  value={resolution.target_system}
                />

              </div>
            </div>

          </div>
        )}

      </div>
    </main>
  );
}

function Card({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="mt-2 text-xl font-semibold">
        {value}
      </p>
    </div>
  );
}

function Info({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 font-medium">
        {value}
      </p>
    </div>
  );
}