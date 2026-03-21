# `nDimenziosKocka(N)` — Detailed Explanation

---

## What it builds

The adjacency matrix of an **N-dimensional hypercube graph**. Each node is a corner of the hypercube, each edge is a connection between two corners that differ by exactly one coordinate.

- 1D: 2 nodes, 1 edge (a line segment)
- 2D: 4 nodes, 4 edges (a square)
- 3D: 8 nodes, 12 edges (a cube)
- ND: 2^N nodes

---

## The recursion formula

The matrix is built from the block structure:

```
M_N = | M_{N-1}  I      |
      | I        M_{N-1} |
```

Which in Kronecker product form is:

```
M_N = kron(I_2, M_{N-1}) + kron(sigma_x, I_{size})
```

where `I_2` is the 2×2 identity, `sigma_x` is the 2×2 flip matrix, and `I_{size}` is the 2^(N-1) × 2^(N-1) identity.

---

## Line by line

```python
def nDimenziosKocka(N: int) -> scisp.csr_matrix:
```
Takes a positive integer `N` (dimension), returns a **CSR sparse matrix** — a memory-efficient format that only stores non-zero values, crucial here since hypercube adjacency matrices are very sparse (each node has exactly N neighbours out of 2^N total).

---

```python
if N == 1:
    return scisp.csr_matrix(np.array([[0, 1],
                                      [1, 0]]))
```
**Base case.** The 1D hypercube is just two nodes connected by one edge:
- Node 0 connects to node 1 → `A[0][1] = 1`
- Node 1 connects to node 0 → `A[1][0] = 1`
- No self-connections → diagonal is 0

The `np.array(...)` dense matrix is immediately wrapped into a `csr_matrix` to stay in sparse format throughout.

---

```python
M_prev = nDimenziosKocka(N - 1)
```
**Recursive call.** Fetches the already-computed adjacency matrix of the (N−1)-dimensional cube. This is the engine of the recursion — each dimension builds on the previous one all the way down to the base case.

---

```python
size = M_prev.shape[0]
```
`M_prev` is a 2^(N-1) × 2^(N-1) matrix, so `size = 2^(N-1)`. This is needed to construct the matching identity matrix below.

---

```python
I = scisp.identity(size, format='csr')
```
Creates a **2^(N-1) × 2^(N-1) sparse identity matrix**. This represents the off-diagonal blocks of `M_N` — the connections between the two "halves" of the hypercube (nodes that differ only in the new Nth coordinate).

---

```python
sigma_x = scisp.csr_matrix(np.array([[0, 1],
                                     [1, 0]]))
```
The **Pauli-X / bit-flip matrix**. In the Kronecker product it acts as the "selector" that places `I` in the off-diagonal blocks and zeros on the diagonal blocks — encoding the new edges introduced by the extra dimension.

---

```python
M_N = scisp.kron(scisp.identity(2, format='csr'), M_prev, format='csr')
     + scisp.kron(sigma_x, I, format='csr')
```
The core construction, two Kronecker products added together:

| Term | Result | Meaning |
|---|---|---|
| `kron(I_2, M_prev)` | block-diagonal `[[M_prev, 0], [0, M_prev]]` | Intra-half edges — connections that already existed in the (N−1)D cube, replicated for both halves |
| `kron(sigma_x, I)` | off-diagonal `[[0, I], [I, 0]]` | Inter-half edges — the new edges connecting each node in one half to its mirror in the other half |

Their sum gives exactly the required block matrix `[[M_prev, I], [I, M_prev]]`.

The `format='csr'` argument on `kron` is **critical** — without it, scipy's `kron` returns a less efficient sparse format that has a bug preventing it from working correctly above N=14.

---

```python
return M_N
```
Returns the fully assembled sparse CSR adjacency matrix, which becomes `M_prev` in the next level of the recursion.

---

## Step-by-step matrix construction

### N=1 — Base case

```
M_1 = [0, 1]
      [1, 0]
```
Two nodes, one edge. Node 0 ↔ Node 1.

---

### N=2 — First recursive step

`M_prev = M_1` (2×2), `size = 2`

```
I       = [1, 0]      sigma_x = [0, 1]
          [0, 1]                [1, 0]
```

**Term 1:** `kron(I_2, M_prev)` — places `M_1` on the diagonal, zeros elsewhere:
```
kron([1,0], M_1) = [M_1,  0 ] = [0,1, 0,0]
    ([0,1]         [ 0 , M_1]   [1,0, 0,0]
                                [0,0, 0,1]
                                [0,0, 1,0]
```

**Term 2:** `kron(sigma_x, I)` — places `I` on the off-diagonal:
```
kron([0,1], I_2) = [ 0 , I_2] = [0,0, 1,0]
    ([1,0]         [I_2,  0 ]   [0,0, 0,1]
                                [1,0, 0,0]
                                [0,1, 0,0]
```

**Sum → M_2:**
```
M_2 = [0,1, 1,0]     which is:    [M_1, I ]
      [1,0, 0,1]                   [ I, M_1]
      [1,0, 0,1]
      [0,1, 1,0]
```
Nodes: 00, 01, 10, 11 — a square. Each node connects to its 2 neighbours differing by one bit.

---

### N=3 — Second recursive step

`M_prev = M_2` (4×4), `size = 4`, `I = I_4`

**Term 1:** `kron(I_2, M_2)` → block diagonal:
```
[M_2,  0 ]
[ 0 , M_2]
```

**Term 2:** `kron(sigma_x, I_4)` → block off-diagonal:
```
[ 0 , I_4]
[I_4,  0 ]
```

**Sum → M_3** (8×8):
```
[M_2, I_4]
[I_4, M_2]
```

---

### The pattern, generalized

At every step the new matrix just wraps the previous one in the same shell:

```
N=1           N=2                  N=3
              ┌──────┬──────┐      ┌──────────┬──────────┐
[0, 1]   →   │  M_1 │  I_2 │  →  │    M_2   │    I_4   │
[1, 0]       │  I_2 │  M_1 │     │    I_4   │    M_2   │
              └──────┴──────┘      └──────────┴──────────┘
  2×2              4×4                      8×8
```

```
N=4                        N=5 ...
┌──────────────┬──────────────┐
│      M_3     │     I_8      │
│      I_8     │     M_3      │
└──────────────┴──────────────┘
             16×16
```

Each shell adds one dimension's worth of edges:
- The two `M_prev` diagonal blocks = **all old edges**, duplicated for both halves
- The two `I` off-diagonal blocks = **all new edges**, each node connecting to its mirror in the new dimension

---

### Node count & eigenvalue spectrum

| N | Nodes (2^N) | Edges | Eigenvalues |
|---|---|---|---|
| 1 | 2 | 1 | −1, +1 |
| 2 | 4 | 4 | −2, 0, 0, +2 |
| 3 | 8 | 12 | −3, −1, −1, −1, +1, +1, +1, +3 |
| N | 2^N | N·2^(N-1) | −N … +N in steps of 2 |

The eigenvalues of `M_N` are always exactly `{N − 2k : k = 0, 1, …, N}`, which is why the 8D cube's 10 smallest are `−8, −6, −6, −6, −6, −6, −6, −6, −6, −4`.

---

## Function specification

For anyone wanting to independently implement `nDimenziosKocka`.

### Signature

```python
def nDimenziosKocka(N: int) -> scipy.sparse.csr_matrix
```

### Parameters

| Parameter | Type | Constraint | Description |
|---|---|---|---|
| `N` | `int` | N ≥ 1 | Dimension of the hypercube |

### Return value

A **CSR sparse matrix** of shape `(2^N, 2^N)` representing the adjacency matrix of the N-dimensional hypercube graph.

- Entry `[i, j] = 1` if nodes `i` and `j` are connected (differ by exactly one bit in their binary representation)
- Entry `[i, j] = 0` otherwise
- The matrix is **symmetric**, **hollow** (zero diagonal), and each row sums to exactly `N`

### Requirements

- Must use `scipy.sparse` throughout — no converting to dense (`numpy`) arrays mid-computation
- All intermediate matrices must stay in `csr` format
- `kron` must be called with `format='csr'` explicitly to avoid a scipy bug above N=14

### Algorithm (pseudocode)

```
function nDimenziosKocka(N):

    if N == 1:
        return csr([[0, 1],
                    [1, 0]])

    M_prev = nDimenziosKocka(N - 1)       # 2^(N-1) × 2^(N-1)
    size   = M_prev.shape[0]              # = 2^(N-1)

    I       = sparse_identity(size)       # size × size
    sigma_x = csr([[0, 1], [1, 0]])       # 2 × 2

    return kron(I_2, M_prev) + kron(sigma_x, I)
```

### Verification

The 10 algebraically smallest eigenvalues of `nDimenziosKocka(8)` must be:

```
[-8, -6, -6, -6, -6, -6, -6, -6, -6, -4]
```

Compute with `scipy.sparse.linalg.eigsh(M, k=10, which='SA')`.

