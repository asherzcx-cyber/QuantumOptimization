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

The expression inside the sum is $1$ when at least one selected station covers neighborhood $j$. This implementation minimizes the negative of this value, so a more negative cost represents better coverage.

## Classical Brute-Force Method

We utilized a simple brute-force method as a classical representation of optimization. We intended to use it as a comparison tool as well as a way to assess the accuracy of early models for our quantum circuit.

## Quantum approach

Our primary approach involved transitioning between the cost function and a Hamiltonian. To effectively implement this, we substituted $x_i = \frac{1}{2}(I - Z_i)$ for every $x$.

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
