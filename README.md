# Quantum Optimization for Fire Station Placement

Our project utilizes a Hamiltonian-based optimizer to find the maximum population coverage of a set quantity of fire stations within a fixed number of neighborhoods. Given a set of candidate station locations and a set of weighted neighborhoods by population, the goal is to choose a specific placement of fire stations that cover as much of the population as possible.

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

We utilized a simple brute-force method as a classical representation of optimization. We utilized it as a comparison tool as well as a way to assess the accuracy of early models for our quantum circuit.

## Quantum approach
 
Our primary approach involves transitioning between the cost function and a Hamiltonian. To effectively implement this, we substituted $x_i = \frac{1}{2}(I - Z_i)$ for every $x$. Since the Hamiltonian is a measure of the total energy of our system, the lowest energy would therefore be the most optimal. Just like with our cost function, this is the most negative output.

Using Python, we created a function that converts from our cost equation to the related Hamiltonian $H_C$. We then defined an ansatz using XY gates with parameters $\theta$ to obtain a probability for all possible outcomes. Using a Variational Quantum Eigensolver (VQE), we repeatedly adjusted the parameters to obtain the optimal circuit. As a result, we obtained the values for the parameter $\theta$ that give the optimal solution the greatest probability.

## Running on IBM Quantum hardware

When running on actual IBM Quantum hardware, we experienced results resembling our simulated outcomes. Although some noise was present, it was nowhere near strong enough to actually skew the results, even in more complex systems (large n and increased weights). As a result, our system is functional on the latest quantum hardware and can be applied successfully.

## Scalibility

The primary feature of our system is its scalability. Since n, w, and a are all parameters, we have defined our code such that it will take any set of matching parameters and modify both the Hamiltonian and the ansatz to represent the system accurately. As a result, our model can be easily scaled to higher orders with little difficulty. Users are therefore able to explore multiple configurations while still receiving the optimal output.

## Generalization

Because our model followed a simple step-by-step process, it can be easily generalized to most binary systems that can be modeled with a discrete cost function. Examples we considered were EEG Electrode Selection, Package Delivery Routing, and Dutch Auctions. Our approach is both easy to use and understand, allowing a convenient approach to optimization that is both effective and efficient.

## Future Implementations

As of right now, current quantum hardware does not support computing power at the scale at which our approach can outpace traditional classical computing. However, our process shows that it is indeed possible to build functional models that can be scaled to larger sizes quickly and efficiently for when such computing power is available. Further improvements that can be made to our code would be runtime efficiency and organization, further streamlining our method. We feel that a user-friendly interface would be very beneficial in outlining our process and making it even easier to understand.
