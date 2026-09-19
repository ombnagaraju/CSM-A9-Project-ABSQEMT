"""
execute_ibm_qem.py
Robust IBM Quantum Runtime SamplerV2 execution helper.

Designed for Qiskit 2.x / modern qiskit-ibm-runtime.
No API secrets are stored in this file.

Usage:
    1. Authenticate separately:
       from qiskit_ibm_runtime import QiskitRuntimeService
       service = QiskitRuntimeService()
    2. Load backend:
       backend = service.backend("ibm_kingston")
    3. Transpile circuit and call:
       job = submit_sampler_v2(backend, [circuit], shots=4096)

IBM's current documentation specifies SamplerV2.run(pubs, *, shots=...)
and recommends passing a BackendV2 as the execution mode.  See:
https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/sampler-v2
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Iterable

import qiskit
from qiskit import QuantumCircuit, transpile


def software_versions() -> dict:
    info = {"qiskit": getattr(qiskit, "__version__", "unknown")}
    try:
        import qiskit_ibm_runtime
        info["qiskit_ibm_runtime"] = getattr(
            qiskit_ibm_runtime, "__version__", "unknown"
        )
    except Exception:
        info["qiskit_ibm_runtime"] = "not-importable"
    return info


def load_service(channel: str | None = None, token: str | None = None):
    """
    Load an already-authenticated IBM Runtime service.

    If channel/token are omitted, QiskitRuntimeService() uses the user's
    locally configured IBM Quantum credentials.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    if channel is None and token is None:
        return QiskitRuntimeService()

    kwargs = {}
    if channel is not None:
        kwargs["channel"] = channel
    if token is not None:
        kwargs["token"] = token
    return QiskitRuntimeService(**kwargs)


def get_backend(service, backend_name: str = "ibm_kingston"):
    backend = service.backend(backend_name)
    if not backend.status().operational:
        raise RuntimeError(f"Backend {backend_name} is not operational.")
    return backend


def prepare_circuit(
    circuit: QuantumCircuit,
    backend,
    optimization_level: int = 3,
    seed_transpiler: int = 42,
) -> QuantumCircuit:
    """Transpile with the target backend and return a hardware-ready circuit."""
    tc = transpile(
        circuit,
        backend=backend,
        optimization_level=optimization_level,
        seed_transpiler=seed_transpiler,
    )
    if tc.num_clbits == 0:
        raise ValueError(
            "Sampler execution requires measurement operations. "
            "Add measurements before submission."
        )
    return tc


def submit_sampler_v2(
    backend,
    circuits: Iterable[QuantumCircuit],
    shots: int = 4096,
    tags: list[str] | None = None,
):
    """Submit one Runtime SamplerV2 job containing one or more circuits."""
    from qiskit_ibm_runtime import SamplerV2

    circuits = list(circuits)
    if not circuits:
        raise ValueError("At least one circuit is required.")

    sampler = SamplerV2(mode=backend)
    if tags is not None:
        # Runtime versions differ in how tags are exposed. Keep tags optional.
        try:
            return sampler.run(circuits, shots=shots, tags=tags)
        except TypeError:
            pass

    return sampler.run(circuits, shots=shots)


def _counts_from_pub(pub_result):
    """
    Extract counts from a SamplerV2 pub result.

    SamplerV2 normally exposes measurement data through pub_result.data.
    The exact register name depends on the circuit. We first prefer the
    conventional 'meas' register and otherwise inspect available fields.
    """
    data = getattr(pub_result, "data", None)
    if data is None:
        raise RuntimeError("Sampler result has no data attribute.")

    # Common Qiskit convention when circuits use measure_all().
    if hasattr(data, "meas"):
        meas = data.meas
        if hasattr(meas, "get_counts"):
            return meas.get_counts()

    # Fall back to the first register exposing get_counts().
    for name in dir(data):
        if name.startswith("_"):
            continue
        try:
            obj = getattr(data, name)
        except Exception:
            continue
        if hasattr(obj, "get_counts"):
            return obj.get_counts()

    raise RuntimeError(
        "Could not locate a classical measurement register with get_counts(). "
        "Inspect job.result()[0].data for the register name."
    )


def extract_counts(job) -> list[dict[str, int]]:
    """Extract one count dictionary per submitted circuit."""
    result = job.result()
    counts = []
    for pub_result in result:
        counts.append(dict(_counts_from_pub(pub_result)))
    return counts


def submit_and_record(
    backend,
    circuits: list[QuantumCircuit],
    circuit_names: list[str],
    shots: int = 4096,
    metadata: dict | None = None,
    output_json: str | Path | None = None,
):
    if len(circuits) != len(circuit_names):
        raise ValueError("circuits and circuit_names must have equal length.")

    t0 = time.time()
    job = submit_sampler_v2(backend, circuits, shots=shots)
    submission_time = time.time()

    record = {
        "backend": backend.name,
        "job_id": job.job_id(),
        "shots": shots,
        "circuit_names": list(circuit_names),
        "qiskit_versions": software_versions(),
        "submitted_unix_time": submission_time,
        "wait_started_unix_time": submission_time,
        "metadata": metadata or {},
    }

    if output_json is not None:
        output_json = Path(output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(record, indent=2), encoding="utf-8")

    return job, record


def wait_and_save_counts(
    job,
    circuit_names: list[str],
    output_json: str | Path,
):
    counts = extract_counts(job)
    result = {
        "job_id": job.job_id(),
        "status": str(job.status()),
        "circuit_names": circuit_names,
        "counts": counts,
    }
    output_json = Path(output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print("IBM QEM runner imported successfully.")
    print(software_versions())
    print(
        "Hardware submission is intentionally not performed by this module "
        "when executed directly."
    )
