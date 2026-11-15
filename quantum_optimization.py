import os
from itertools import combinations
from math import comb

import numpy as np
from qiskit import QuantumCircuit, generate_preset_pass_manager
from qiskit.circuit.library import StatePreparation
from qiskit.quantum_info import SparsePauliOp
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import EstimatorV2, QiskitRuntimeService, SamplerV2
from scipy.optimize import minimize


N_QUBITS = 5
HAMMING_WEIGHT = 2

COVERAGE = np.array(
    [
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
        [0, 1, 0, 1, 0, 0, 0, 0, 1, 1],
    ]
)
WEIGHTS = np.array([1, 2, 1, 3, 1, 4, 1, 2, 1, 1])


def cost_hamiltonian(coverage, weights):
    """Build the weighted maximum-coverage cost Hamiltonian."""
    coverage = np.asarray(coverage, dtype=float)
    weights = np.asarray(weights, dtype=float)

    if coverage.ndim != 2:
        raise ValueError("coverage must be a 2D array.")

    candidate_count, neighborhood_count = coverage.shape
    if candidate_count < 1 or weights.shape != (neighborhood_count,):
        raise ValueError(
            "Require at least one candidate and one weight per coverage column."
        )

    identity = SparsePauliOp.from_list([("I" * candidate_count, 1.0)])
    hamiltonian = 0.0 * identity

    for neighborhood in range(neighborhood_count):
        product = identity

        for candidate in range(candidate_count):
            if coverage[candidate, neighborhood] == 0:
                continue

            z_operator = SparsePauliOp.from_sparse_list(
                [("Z", [candidate], 1.0)],
                num_qubits=candidate_count,
            )
            coefficient = coverage[candidate, neighborhood]
            factor = (1 - coefficient / 2) * identity + (
                coefficient / 2
            ) * z_operator
            product = product.compose(factor).simplify()

        hamiltonian -= weights[neighborhood] * (identity - product)

    return hamiltonian.simplify()


def fixed_weight_distribution(parameters, n_qubits, hamming_weight):
    """Return basis states and probabilities for a fixed Hamming weight."""
    if not 0 <= hamming_weight <= n_qubits:
        raise ValueError("hamming_weight must be between 0 and n_qubits.")

    basis_indices = [
        sum(1 << qubit for qubit in occupied)
        for occupied in combinations(range(n_qubits), hamming_weight)
    ]
    if parameters.shape != (len(basis_indices) - 1,):
        raise ValueError("Require one logit per fixed-weight state, except one.")

    logits = np.append(parameters, 0.0)
    exponentials = np.exp(logits - np.max(logits))
    probabilities = exponentials / exponentials.sum()
    return basis_indices, probabilities


def build_ansatz(parameters, n_qubits=N_QUBITS, hamming_weight=HAMMING_WEIGHT):
    """Prepare a state supported only on feasible station configurations."""
    basis_indices, probabilities = fixed_weight_distribution(
        np.asarray(parameters, dtype=float),
        n_qubits,
        hamming_weight,
    )
    amplitudes = np.zeros(2**n_qubits, dtype=complex)
    amplitudes[basis_indices] = np.sqrt(probabilities)

    circuit = QuantumCircuit(n_qubits)
    circuit.append(StatePreparation(amplitudes), range(n_qubits))
    return circuit


def run_circuit_and_get_counts(circuit, backend, shots=1000):
    """Measure a circuit on a simulator or IBM Quantum backend."""
    pass_manager = generate_preset_pass_manager(
        backend=backend,
        optimization_level=1,
    )
    measured_circuit = circuit.copy()
    measured_circuit.measure_all()
    isa_circuit = pass_manager.run(measured_circuit)

    sampler = SamplerV2(mode=backend)
    result = sampler.run([isa_circuit], shots=shots).result()
    return result[0].data.meas.get_counts()


def optimize_on_simulator(hamiltonian, simulator):
    """Optimize the fixed-weight state using an Aer estimator."""
    pass_manager = generate_preset_pass_manager(
        backend=simulator,
        optimization_level=1,
    )
    estimator = EstimatorV2(mode=simulator)

    def energy(parameters):
        circuit = build_ansatz(parameters)
        isa_circuit = pass_manager.run(circuit)
        isa_hamiltonian = hamiltonian.apply_layout(isa_circuit.layout)
        result = estimator.run(
            [(isa_circuit, isa_hamiltonian)],
            precision=0.05,
        ).result()
        return float(np.asarray(result[0].data.evs).item())

    initial_parameters = np.zeros(comb(N_QUBITS, HAMMING_WEIGHT) - 1)
    return minimize(
        energy,
        initial_parameters,
        method="COBYLA",
        bounds=[(-12, 12)] * len(initial_parameters),
        options={"maxiter": 600, "rhobeg": 1.0, "tol": 1e-3},
    )


def run_on_ibm_hardware(circuit):
    """Run on IBM hardware when IBM_QUANTUM_TOKEN is configured."""
    token = os.getenv("IBM_QUANTUM_TOKEN")
    if not token:
        print("IBM_QUANTUM_TOKEN is not set; skipping hardware execution.")
        return None

    QiskitRuntimeService.save_account(
        channel="ibm_quantum_platform",
        token=token,
        overwrite=True,
        set_as_default=True,
    )
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
    backend = service.least_busy(
        operational=True,
        simulator=False,
        min_num_qubits=127,
    )
    counts = run_circuit_and_get_counts(circuit, backend, shots=1000)
    print(f"Hardware backend: {backend.name}")
    print(f"Hardware measurement counts: {counts}")
    plot_histogram(counts)
    return counts


def main():
    simulator = AerSimulator()
    hamiltonian = cost_hamiltonian(COVERAGE, WEIGHTS)
    print(hamiltonian)

    optimization = optimize_on_simulator(hamiltonian, simulator)
    print(f"Optimization: {optimization.message}")
    print(f"Optimized energy: {optimization.fun:.6f}")
    print(f"Optimized parameters: {optimization.x}")

    fire_depots = build_ansatz(optimization.x)
    counts = run_circuit_and_get_counts(fire_depots, simulator, shots=1000)
    print(f"Simulator measurement counts: {counts}")
    print(f"Most frequent bitstring: {max(counts, key=counts.get)}")

    run_on_ibm_hardware(fire_depots)


if __name__ == "__main__":
    main()
