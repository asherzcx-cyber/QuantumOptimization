#John's Code with real implementation

import numpy as np
from qiskit.quantum_info import SparsePauliOp
from itertools import combinations
from qiskit import QuantumCircuit, generate_preset_pass_manager
from qiskit.circuit.library import StatePreparation
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise import errors
from math import comb
from scipy.optimize import minimize
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime import EstimatorV2, Sampler
from qiskit_ibm_runtime import SamplerV2 as Sampler, QiskitRuntimeService
from qiskit.visualization import plot_histogram

simulator = AerSimulator()
pass_manager = generate_preset_pass_manager(
    backend=simulator,
    optimization_level=1,
)
estimator = EstimatorV2(mode=simulator)

# Number of candidate locations (qubits)
n_qubits = 5
# Number of fire stations to be built (hamming weight of the bitstring)
hamming_weight = 2

# Array containing the coefficients a_ij for each candidate location i and each neighborhood j
a = np.array([[1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
              [0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
              [0, 1, 0, 1, 0, 0, 0, 0, 1, 1]])
# Array containing the weights (population) w_j for each neighborhood j
w = np.array([1, 2, 1, 3, 1, 4, 1, 2, 1, 1])

def cost_hamiltonian(a, w):
    """
    a[i, j]: coefficient a_ij, with shape (n_qubits, n_items)
    w[j]: weight of item j

    Variable x[i] is represented by qubit i.
    """
    a = np.asarray(a, dtype=float)
    w = np.asarray(w, dtype=float)

    if a.ndim != 2:
        raise ValueError("a must be a 2D array.")

    n, m = a.shape
    if n < 1 or w.shape != (m,):
        raise ValueError("Require n >= 1 and one weight per column of a.")

    identity = SparsePauliOp.from_list([("I" * n, 1.0)])
    H = 0.0 * identity

    for j in range(m):
        product = identity

        for i in range(n):
            if a[i, j] == 0:
                continue

            Zi = SparsePauliOp.from_sparse_list(
                [("Z", [i], 1.0)],
                num_qubits=n,
            )

            # I - a_ij * (I - Z_i)/2
            factor = (1 - a[i, j] / 2) * identity + (a[i, j] / 2) * Zi
            product = product.compose(factor).simplify()

        H = H - w[j] * (identity - product)

    return H.simplify()

H = cost_hamiltonian(a, w)
print(H)


def fixed_weight_distribution(parameters, n_qubits, hamming_weight):
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

# Create the ansatz circuit for the fixed-weight distribution
def build_ansatz(parameters, n_qubits=5, hamming_weight=2):
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

  pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
  measured_circuit = circuit.copy()
  measured_circuit.measure_all()
  isa_circuit = pm.run(measured_circuit)

  sampler = Sampler(mode=backend)

  job = sampler.run([isa_circuit], shots=shots)
  result = job.result()

  return result[0].data.meas.get_counts()

def energy(parameters):
    isa_circuit = pass_manager.run(build_ansatz(parameters, n_qubits=n_qubits, hamming_weight=hamming_weight))
    isa_hamiltonian = H.apply_layout(isa_circuit.layout)
    result = estimator.run(
        [(isa_circuit, isa_hamiltonian)],
        precision=0.05,
    ).result()
    return float(np.asarray(result[0].data.evs).item())

initial_parameters = np.zeros(comb(n_qubits, hamming_weight) - 1)
optimization = minimize(
    energy,
    initial_parameters,
    method="COBYLA",
    bounds=[(-12, 12)] * len(initial_parameters),
    options={"maxiter": 600, "rhobeg": 1.0, "tol": 1e-3},
)

print(f"Optimization: {optimization.message}")
print(f"Optimized energy: {optimization.fun:.6f}")
print(f"Optimized parameters: {optimization.x}")

Fire_Depots = build_ansatz(
    optimization.x,
    n_qubits=n_qubits,
    hamming_weight=hamming_weight,
)
counts = run_circuit_and_get_counts(Fire_Depots, backend=simulator, shots=1000)
print(f"Measurement counts: {counts}")
print(f"Most frequent bitstring: {max(counts, key=counts.get)}")

# Add measurements
measured_circuit = Fire_Depots
measured_circuit.measure_all()

QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token='APIkey', overwrite=True, set_as_default=True)
service = QiskitRuntimeService(channel='ibm_quantum_platform')

service = QiskitRuntimeService()

backend = service.least_busy(operational=True, simulator=False, min_num_qubits=127)

counts = run_circuit_and_get_counts(measured_circuit, backend, shots=1000)

plot_histogram(counts)
