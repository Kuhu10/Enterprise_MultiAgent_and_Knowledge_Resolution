"use client";

import { useState } from "react";

/*
|--------------------------------------------------------------------------
| API Configuration
|--------------------------------------------------------------------------
|
| Local development:
|   http://localhost:8000
|
| Production:
|   NEXT_PUBLIC_API_URL will contain your deployed FastAPI URL.
|
*/

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/*
|--------------------------------------------------------------------------
| Types
|--------------------------------------------------------------------------
*/

type Resolution = {
  incident_id: string;
  incident_type: string;
  root_cause: string;
  recommended_action: string;
  target_system: string;
  confidence_score?: number;
};

/*
|--------------------------------------------------------------------------
| Main Page
|--------------------------------------------------------------------------
*/

export default function Home() {
  const [file, setFile] = useState<File | null>(null);

  const [resolution, setResolution] =
    useState<Resolution | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  /*
  |--------------------------------------------------------------------------
  | Analyze Log
  |--------------------------------------------------------------------------
  */

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

      console.log("Sending log to:", `${API_URL}/analyze`);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      /*
      |--------------------------------------------------------------------------
      | Check API Response
      |--------------------------------------------------------------------------
      */

      if (!response.ok) {
        let message = "Backend returned an error.";

        try {
          const errorData = await response.json();

          message =
            errorData.detail ||
            errorData.message ||
            message;
        } catch {
          // Keep default message
        }

        throw new Error(message);
      }

      /*
      |--------------------------------------------------------------------------
      | Read API Response
      |--------------------------------------------------------------------------
      */

      const data = await response.json();

      console.log("API response:", data);

      if (!data.resolution) {
        throw new Error(
          "Backend response does not contain resolution data."
        );
      }

      setResolution(data.resolution);
    } catch (err) {
      console.error("Analyze error:", err);

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to connect to FastAPI backend.");
      }
    } finally {
      setLoading(false);
    }
  }

  /*
  |--------------------------------------------------------------------------
  | UI
  |--------------------------------------------------------------------------
  */

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto max-w-6xl px-6 py-12">

        {/* Header */}

        <div className="mb-10">
          <p className="mb-2 text-sm font-semibold text-blue-400">
            ENTERPRISE AI OPERATIONS
          </p>

          <h1 className="text-4xl font-bold">
            Multi-Agent Incident Resolution
          </h1>

          <p className="mt-3 max-w-3xl text-slate-400">
            Upload an HDFS log and allow the agent pipeline
            to detect, diagnose and resolve the incident.
          </p>
        </div>

        {/* Log Upload */}

        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-7">

          <h2 className="mb-5 text-xl font-semibold">
            Log Analysis
          </h2>

          <input
            type="file"
            accept=".log,.txt"
            onChange={(e) => {
              const selectedFile =
                e.target.files?.[0] ?? null;

              setFile(selectedFile);

              setResolution(null);

              setError("");
            }}
            className="
              block
              w-full
              rounded-lg
              border
              border-slate-700
              bg-slate-950
              p-3
            "
          />

          {file && (
            <div className="mt-3">
              <p className="text-sm text-slate-400">
                Selected:
                <span className="ml-2 font-medium text-slate-200">
                  {file.name}
                </span>
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Size: {(file.size / 1024).toFixed(2)} KB
              </p>
            </div>
          )}

          <button
            onClick={analyzeLog}
            disabled={loading || !file}
            className="
              mt-5
              rounded-lg
              bg-blue-600
              px-6
              py-3
              font-semibold
              transition
              hover:bg-blue-500
              disabled:cursor-not-allowed
              disabled:opacity-50
            "
          >
            {loading
              ? "Analyzing..."
              : "Analyze Incident"}
          </button>

          {/* Loading */}

          {loading && (
            <div className="mt-5 rounded-lg border border-blue-900 bg-blue-950/40 p-4">
              <p className="text-blue-300">
                Analyzing HDFS log...
              </p>

              <p className="mt-1 text-sm text-slate-400">
                The incident detection service is processing
                the uploaded log.
              </p>
            </div>
          )}

          {/* Error */}

          {error && (
            <div className="mt-5 rounded-lg border border-red-900 bg-red-950 p-4">
              <p className="font-semibold text-red-300">
                Analysis failed
              </p>

              <p className="mt-1 text-sm text-red-300">
                {error}
              </p>
            </div>
          )}
        </div>

        {/* Incident Result */}

        {resolution && (
          <div className="mt-8">

            {/* Incident Header */}

            <div className="mb-5 flex items-center justify-between">

              <h2 className="text-2xl font-bold">
                Incident Detected
              </h2>

              <span
                className="
                  rounded-full
                  bg-red-950
                  px-4
                  py-2
                  text-sm
                  font-semibold
                  text-red-300
                "
              >
                DETECTED
              </span>

            </div>

            {/* Summary Cards */}

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

            {/* Agent Diagnosis */}

            <div
              className="
                mt-5
                rounded-2xl
                border
                border-slate-800
                bg-slate-900
                p-7
              "
            >

              <h3 className="text-lg font-semibold">
                Agent Diagnosis
              </h3>

              <p className="mt-1 text-sm text-slate-400">
                Analysis generated by the incident detection
                pipeline.
              </p>

              <div className="mt-6 space-y-5">

                <Info
                  label="Incident ID"
                  value={resolution.incident_id}
                />

                <Info
                  label="Incident Type"
                  value={resolution.incident_type}
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

            {/* Pipeline */}

            <div
              className="
                mt-5
                rounded-2xl
                border
                border-slate-800
                bg-slate-900
                p-7
              "
            >

              <h3 className="text-lg font-semibold">
                Agent Pipeline
              </h3>

              <div className="mt-6 grid gap-4 md:grid-cols-4">

                <PipelineStep
                  number="1"
                  title="Log Upload"
                  status="Completed"
                />

                <PipelineStep
                  number="2"
                  title="Detection"
                  status="Completed"
                />

                <PipelineStep
                  number="3"
                  title="Execution"
                  status="Pending"
                />

                <PipelineStep
                  number="4"
                  title="Verification"
                  status="Pending"
                />

              </div>

            </div>

          </div>
        )}

        {/* Footer */}

        <div className="mt-10 border-t border-slate-800 pt-6">
          <p className="text-sm text-slate-500">
            Multi-Agent Incident Resolution System
          </p>
        </div>

      </div>
    </main>
  );
}

/*
|--------------------------------------------------------------------------
| Card Component
|--------------------------------------------------------------------------
*/

function Card({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-800
        bg-slate-900
        p-6
      "
    >

      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="mt-2 text-xl font-semibold">
        {value}
      </p>

    </div>
  );
}

/*
|--------------------------------------------------------------------------
| Information Component
|--------------------------------------------------------------------------
*/

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

      <p className="mt-1 break-words font-medium">
        {value}
      </p>

    </div>
  );
}

/*
|--------------------------------------------------------------------------
| Pipeline Component
|--------------------------------------------------------------------------
*/

function PipelineStep({
  number,
  title,
  status,
}: {
  number: string;
  title: string;
  status: string;
}) {
  const completed = status === "Completed";

  return (
    <div
      className="
        rounded-xl
        border
        border-slate-800
        bg-slate-950
        p-4
      "
    >

      <div className="flex items-center gap-3">

        <div
          className="
            flex
            h-8
            w-8
            items-center
            justify-center
            rounded-full
            bg-blue-600
            text-sm
            font-bold
          "
        >
          {number}
        </div>

        <p className="font-semibold">
          {title}
        </p>

      </div>

      <p
        className={
          completed
            ? "mt-3 text-sm text-green-400"
            : "mt-3 text-sm text-slate-500"
        }
      >
        {status}
      </p>

    </div>
  );
}