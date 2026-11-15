# Quantum Optimization for Fire Station Placement

Our project explores a weighted **maximum coverage** problem for maximizing the coverage in terms of population by fire stations. Given a set of candidate station locations and a set of weighted neighborhoods by population, the goal is to choose a specific number of fire stations that cover as much of the population as possible.

We utilize a Hamiltonian representation of the cost function to optimize our model.

The project includes two approaches:

- A classical brute-force search that checks every possible station configuration.
- A Qiskit-based variational quantum approach that applies quantum properties for optimization.

## Optimization model

Let:

- $n$ be the number of candidate fire station locations.
- $m$ be the number of neighborhoods.
- $x_i = 1$ when a station is placed at candidate location $i$, and $x_i = 0$ otherwise.
- $a_{ij} = 1$ when location $i$ covers neighborhood $j$, and $a_{ij} = 0$ otherwise.
- $w_j$ be the weight of neighborhood $j$, such as its population or relative priority.
- $K$ be the number of stations that can be built.

The weighted coverage objective is:

$$
\max_{\mathbf{x} \in \{0,1\}^{n}}
\quad
\sum_{j=1}^{m} w_j
\left(1 - \prod_{i=1}^{n}\left(1-a_{ij}x_i\right)\right)
$$

subject to:

$$
\sum_{i=1}^{n} x_i = K
$$

The expression inside the sum is $1$ when at least one selected station covers neighborhood $j$. The implementation minimizes the negative of this value, so a more negative cost represents better coverage.

## Classical exhaustive search

The classical program checks all $2^n$ binary station configurations. For each configuration, it calculates the total covered weight and keeps the best solution that uses no more than the allowed number of stations.

The program asks for four inputs:

1. $n$: number of candidate station locations.
2. `maxFires`: maximum number of stations to build.
3. $a$: the coverage matrix, with rows separated by `$` and values separated by commas.
4. $w$: comma-separated neighborhood weights.

For example, the five-location, ten-neighborhood instance used by the quantum implementation can be entered as:

```text
Please enter your n value: 5
Please enter the max fire station num: 2
Please enter your a string: 1,1,1,0,0,0,0,0,0,0$0,0,1,1,1,1,0,0,0,0$0,0,0,0,0,1,1,0,0,0$0,0,0,0,0,0,0,1,1,1$0,1,0,1,0,0,0,0,1,1
Please enter your w string: 1,2,1,3,1,4,1,2,1,1
```

The output contains:

- A binary string describing the selected station locations. A $1$ means that the corresponding location is selected.
- The negative weighted coverage score. For example, $-15$ means the selected stations cover neighborhoods with a total weight of $15$.

Because exhaustive search evaluates every binary configuration, its time complexity is $O\!\left(2^n n m\right)$. It is useful as an exact baseline for small problem instances but becomes impractical as $n$ grows.

## Quantum approach

The quantum implementation converts the coverage objective into a diagonal cost Hamiltonian using Qiskit's `SparsePauliOp`.

Its ansatz prepares a probability distribution over only the basis states whose Hamming weight equals the desired number of fire stations. This enforces an exact station count directly in the quantum state. A classical COBYLA optimizer then updates the ansatz parameters to minimize the expected energy.

The workflow is:

1. Build the weighted-coverage cost Hamiltonian.
2. Generate all basis states with the required Hamming weight.
3. Prepare a parameterized distribution over those states.
4. Estimate the Hamiltonian expectation value with Qiskit Aer.
5. Optimize the parameters with COBYLA.
6. Measure the optimized circuit and select the most frequent bitstring.
7. Optionally run the measured circuit on IBM Quantum hardware.

The current quantum example uses five candidate locations and selects exactly two stations. Unlike the classical constraint $\sum_{i=1}^{n}x_i \le K$, the fixed-weight quantum ansatz enforces $\sum_{i=1}^{n}x_i = K$.

## Installation

Python 3.10 or newer is recommended. Install the packages used by the quantum implementation with:

```bash
python -m pip install -r requirements.txt
```

Run the simulator with:

```bash
python quantum_optimization.py
```

The classical exhaustive-search version only uses Python's standard library. It should include:

```python
import time
```

before calling `time.perf_counter()`.

## Running on IBM Quantum hardware

An IBM Quantum account is required for real-device execution. Never commit an API token to this repository. Store the token in an environment variable instead:

```bash
export IBM_QUANTUM_TOKEN="your-token"
```

Then configure Qiskit in Python:

```python
import os
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token=os.environ["IBM_QUANTUM_TOKEN"],
    overwrite=True,
    set_as_default=True,
)
service = QiskitRuntimeService(channel="ibm_quantum_platform")
```

After authentication, the program can select an operational hardware backend and sample the optimized circuit. Hardware results may differ from simulator results because of device noise and calibration conditions.

If `IBM_QUANTUM_TOKEN` is not set, the program runs the simulator normally and skips the hardware step.

## Notes

- Every row of $a$ must contain the same number of entries.
- The number of rows in $a$ must equal $n$.
- The number of weights in $w$ must equal the number of columns in $a$.
- Coverage values should normally be binary ($0$ or $1$).
- Neighborhood weights should be non-negative integers or real values.
- The quantum Hamming weight must be between $0$ and $n$.

## Future improvements

- Add command-line arguments or structured input files instead of interactive strings.
- Validate malformed matrix and weight inputs.
- Compare classical and quantum results automatically on the same instance.
- Add circuit-depth, execution-time, and approximation-quality benchmarks.
- Test alternative constrained ansatzes that avoid full state preparation.

## License

Add a license file before redistributing or reusing this project.
