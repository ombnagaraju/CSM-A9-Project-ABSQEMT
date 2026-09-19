"""
Adaptive QEM selector for the Adaptive_QEM_IBM project.

This is the first transparent, rule-based version of the adaptive
quantum-error-mitigation decision engine. It selects among raw execution,
readout-error mitigation, ZNE, and a combined strategy using circuit
complexity and current hardware-noise indicators.

The selector does not execute hardware jobs and does not perform mitigation;
it only produces a reproducible strategy decision.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class CircuitFeatures:
    qubits: int
    depth: int
    cx_count: int = 0
    cz_count: int = 0
    swap_count: int = 0
    one_qubit_gate_count: int = 0
    two_qubit_gate_count: int = 0

    @property
    def two_qubit_density(self) -> float:
        return self.two_qubit_gate_count / self.depth if self.depth > 0 else 0.0


@dataclass
class HardwareFeatures:
    readout_error: float = 0.0
    one_qubit_error: float = 0.0
    two_qubit_error: float = 0.0
    t1_seconds: Optional[float] = None
    t2_seconds: Optional[float] = None


@dataclass
class AdaptiveDecision:
    method: str
    confidence: float
    reason: str
    circuit_features: Dict[str, Any]
    hardware_features: Dict[str, Any]
    scores: Dict[str, float]


class AdaptiveQEMSelector:
    """
    Transparent rule-based adaptive selector.

    The thresholds are explicit experimental parameters and should be
    validated/tuned using training or calibration data before being frozen
    for the final publication experiment.
    """

    def __init__(
        self,
        readout_threshold: float = 0.02,
        two_qubit_error_threshold: float = 0.01,
        depth_threshold: int = 50,
        cx_threshold: int = 20,
        high_depth_threshold: int = 100,
        high_cx_threshold: int = 50,
        raw_noise_threshold: float = 0.005,
    ):
        self.readout_threshold = readout_threshold
        self.two_qubit_error_threshold = two_qubit_error_threshold
        self.depth_threshold = depth_threshold
        self.cx_threshold = cx_threshold
        self.high_depth_threshold = high_depth_threshold
        self.high_cx_threshold = high_cx_threshold
        self.raw_noise_threshold = raw_noise_threshold

    def _validate(self, circuit: CircuitFeatures, hardware: HardwareFeatures):
        if circuit.qubits < 1:
            raise ValueError("circuit.qubits must be >= 1")
        if circuit.depth < 0:
            raise ValueError("circuit.depth cannot be negative")

        for name in ("readout_error", "one_qubit_error", "two_qubit_error"):
            value = getattr(hardware, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")

    def score(
        self,
        circuit: CircuitFeatures,
        hardware: HardwareFeatures,
    ) -> Dict[str, float]:
        """Return transparent strategy scores; scores are not probabilities."""
        self._validate(circuit, hardware)

        raw = 1.0
        readout = 0.0
        zne = 0.0

        if hardware.readout_error >= self.readout_threshold:
            readout += 3.0
        elif hardware.readout_error >= self.readout_threshold / 2:
            readout += 1.5

        if hardware.two_qubit_error >= self.two_qubit_error_threshold:
            zne += 3.0
        elif hardware.two_qubit_error >= self.two_qubit_error_threshold / 2:
            zne += 1.5

        if circuit.depth >= self.high_depth_threshold:
            zne += 3.0
        elif circuit.depth >= self.depth_threshold:
            zne += 1.5

        if circuit.cx_count >= self.high_cx_threshold:
            zne += 3.0
        elif circuit.cx_count >= self.cx_threshold:
            zne += 1.5

        if circuit.swap_count > 0:
            zne += min(2.0, 0.5 * circuit.swap_count)

        combined = readout + zne if readout >= 3.0 and zne >= 3.0 else 0.0

        total_noise = max(
            hardware.readout_error,
            hardware.one_qubit_error,
            hardware.two_qubit_error,
        )

        if total_noise > self.raw_noise_threshold:
            raw = max(0.0, raw - 1.0)

        if circuit.depth >= self.depth_threshold:
            raw = max(0.0, raw - 1.0)

        if circuit.cx_count >= self.cx_threshold:
            raw = max(0.0, raw - 1.0)

        return {
            "raw": raw,
            "readout_mitigation": readout,
            "zne": zne,
            "readout_mitigation+zne": combined,
        }

    def select(
        self,
        circuit: CircuitFeatures,
        hardware: HardwareFeatures,
    ) -> AdaptiveDecision:
        scores = self.score(circuit, hardware)

        method = max(scores, key=scores.get)
        best = scores[method]
        ordered = sorted(scores.values(), reverse=True)
        second = ordered[1]

        if best <= 0:
            method = "raw"
            best = scores["raw"]

        confidence = min(
            1.0,
            max(0.0, (best - second) / max(best, 1.0)),
        )

        reasons = {
            "readout_mitigation": (
                "Readout assignment error is sufficiently high to justify "
                "measurement-error mitigation."
            ),
            "zne": (
                "Circuit depth/two-qubit-gate exposure and hardware "
                "two-qubit noise indicate increased gate-error sensitivity."
            ),
            "readout_mitigation+zne": (
                "Both readout error and gate/depth-related noise are "
                "substantial, so combined mitigation is selected."
            ),
            "raw": (
                "Estimated noise and circuit complexity are low enough "
                "that raw execution has the lowest mitigation burden."
            ),
        }

        return AdaptiveDecision(
            method=method,
            confidence=confidence,
            reason=reasons[method],
            circuit_features=asdict(circuit),
            hardware_features=asdict(hardware),
            scores=scores,
        )

    def select_from_dict(
        self,
        circuit_features: Dict[str, Any],
        hardware_features: Dict[str, Any],
    ) -> AdaptiveDecision:
        return self.select(
            CircuitFeatures(**circuit_features),
            HardwareFeatures(**hardware_features),
        )


def adaptive_qem_decision(
    circuit_features: Dict[str, Any],
    hardware_features: Dict[str, Any],
    **selector_kwargs: Any,
) -> Dict[str, Any]:
    """Serializable functional interface for notebooks and batch analysis."""
    selector = AdaptiveQEMSelector(**selector_kwargs)
    return asdict(
        selector.select_from_dict(
            circuit_features,
            hardware_features,
        )
    )


if __name__ == "__main__":
    selector = AdaptiveQEMSelector()

    decision = selector.select(
        CircuitFeatures(
            qubits=5,
            depth=80,
            cx_count=28,
            two_qubit_gate_count=28,
        ),
        HardwareFeatures(
            readout_error=0.022,
            one_qubit_error=0.0005,
            two_qubit_error=0.012,
        ),
    )

    print("Adaptive QEM decision")
    print("---------------------")
    print("Method    :", decision.method)
    print("Confidence:", round(decision.confidence, 4))
    print("Reason    :", decision.reason)
    print("Scores    :", decision.scores)
