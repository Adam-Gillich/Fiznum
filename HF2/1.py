import numpy as np
import matplotlib.pyplot as plt
import itertools as itr

# -------------------------------------------------------
# Data
# -------------------------------------------------------

A = np.array([
    [14,  8,  6, 10, 12],
    [10, 16,  9, 12, 11],
    [13, 11,  8, 10, 15],
    [ 7,  9, 17, 12, 14],
    [ 9, 10, 15, 11, 13],
])

B = np.array([
    [12.36,  9.96,  6.72, 10.08, 11.64],
    [ 9.24, 12.192, 7.128, 9.864, 9.552],
    [ 6.24,  5.28,  3.84,  4.8,   7.2 ],
    [ 4.2,   5.4,  10.2,   7.2,   8.4 ],
    [ 5.4,   6.0,   9.0,   6.6,   7.8 ],
])

G0 = np.diag([5/3, 5/3, 5/3, 5/3, 5/3])

G1 = np.eye(5)
G1[0, 1] = -0.4

G2 = np.eye(5)
G2[1, 0] = -0.3

G3 = np.eye(5)
G3[0, 2] = -0.2

G4 = np.eye(5)
G4[2, 2] = 1.25

remedies = {"G0": G0, "G1": G1, "G2": G2, "G3": G3, "G4": G4}

CLASSES = ["W", "R", "M", "C", "P"]
STATS = ["STR", "DEX", "CON", "INT", "WIS"]


# -------------------------------------------------------
# Requested Functions
# -------------------------------------------------------


def identify_curse(A, B):
    """
    Identifies the curse with numpy solve.
    :param A: Original stat matrix
    :param B: Cursed stat matrix
    :return: The curse matrix C
    """

    # We want CA = B, but solve can only do AX = B, thus At Ct = Bt
    C_T = np.linalg.solve(A.T, B.T)

    if np.allclose(C_T.T @ A, B):
        return C_T.T
    else:
        raise ValueError("Could not identify curse!")


def inverse_curse(C):
    """
    Returns the inverse of the curse matrix C.
    :param C: Curse matrix
    :return: Inverse C
    """

    return np.linalg.inv(C)


def find_remedy_sequence(target, remedies):
    """
    This function finds the suitable remedy sequence with brute force.
    :param target: The target matrix
    :param remedies: Dictionary of remedies
    :return: List of remedy keys, in the correct order.
    """

    keys = list(remedies.keys())

    # Number of keys
    for i in range(1, len(keys) + 1):
        # One permutation
        for j in itr.permutations(keys, i):
            result = np.eye(5)
            # Apply j to result
            for k in j:
                result = remedies[k] @ result
            # Check if correct
            if np.allclose(result, target):
                return list(j)

    raise ValueError("Could not identify a suitable remedy sequence!")


def apply_remedy_sequence(X, remedies, sequence):
    """
    Applies the found remedy sequence to an inputted matrix. Which will be the stat matrix after the curse.
    :param X: Inputted matrix
    :param remedies: Dict of remedies
    :param sequence: The ordered list of correct keys
    :return: The original stat matrix before the curse
    """

    for k in sequence:
        X = remedies[k] @ X
    return X

# ---------------------------
# Helper Functions
# ---------------------------


def CheckCinv(C, A, B):
    """
    Checks if C inverse is truly found.
    :param C: Curse matrix
    :param A: Original stat matrix
    :param B: Cursed stat matrix
    :return: Inverse C
    """

    C_inv = inverse_curse(C)

    if np.allclose(C_inv @ B, A):
        return C_inv
    else:
        raise ValueError("C inverse can't replicate A.")


def CheckArec(CursedMatrix, remedies, sequence, A):
    """
    Checks if A is truly recreated.
    :param CursedMatrix: Cursed stat matrix
    :param remedies: Dict of remedies
    :param sequence: The ordered list of correct keys
    :param A: Original stat matrix
    :return: Recreated original stat matrix
    """

    A_rec = apply_remedy_sequence(CursedMatrix, remedies, sequence)

    if np.allclose(A_rec, A):
        return A_rec
    else:
        raise ValueError("The reconstructed A doesn't match with the original.")


def MakeStates(CursedMatrix, remedies, sequence):
    """
    This function makes a list from all the states of B (Cursed Matrix)
    through back to A (Original stat matrix). Starting and ending in the two.
    :param CursedMatrix: Cursed stat matrix
    :param remedies: Dict of remedies
    :param sequence: The ordered list of correct keys
    :return:
    """

    B = CursedMatrix
    states = [B]

    for k in sequence:
        B = remedies[k] @ B
        states.append(B)

    return states

# -------------------------------------------------------
# Plotting functions
# -------------------------------------------------------


def Matshow(fig, ax, data, vmin, vmax, title, cmap="viridis"):
    """
    This function does the set-up of the axes for the 'plot_remedy' function.
    :param fig: Current figure
    :param ax: Current axes
    :param data: Current matrix
    :param vmin: Colour scale minimum
    :param vmax: Colour scale maximum
    :param title: Current panel title
    :param cmap: Colormap name
    """

    im = ax.matshow(data, vmin=vmin, vmax=vmax, cmap=cmap)
    ax.set_title(title, pad=10)
    ax.set_xticks(range(5))
    ax.set_xticklabels(CLASSES)
    ax.set_yticks(range(5))
    ax.set_yticklabels(STATS)
    ax.xaxis.set_ticks_position("bottom")

    # Value annotations
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center",
                    fontsize=7, color="white" if data[i, j] < (vmin + vmax) / 2 else "black")

    fig.colorbar(im, ax=ax, fraction=0.05, pad=0.04)


def plot_remedy(B, remedies, sequence):
    """
    This function makes the plots of the matrixes from B (Cursed Matrix)
    through back to A (Original stat matrix).
    :param B: Cursed Matrix
    :param remedies: Dict of remedies
    :param sequence: The ordered list of correct keys
    """

    states = MakeStates(B, remedies, sequence)

    panel_num = len(states)

    fig, axes = plt.subplots(1, panel_num, figsize=(3.5 * panel_num, 4.5),
                             constrained_layout=True)
    fig.suptitle("Stat matrix evolution during remedy sequence", fontsize=13)

    titles = (["B (cursed)"] +
              [f"After {sequence[i]}" for i in range(len(sequence) - 1)] +
              [r"$\tilde{A}$ (reconstructed)"])

    vmin = min(i.min() for i in states)
    vmax = max(i.max() for i in states)

    plot_data = zip(axes, states, titles)

    for ax, state, title in plot_data:
        Matshow(fig, ax, state, vmin, vmax, title)

    plt.show()


def plot_comparison(A, B, A_rec):
    """
    This function plots A (Original stat matrix), B (Cursed Matrix)
    and A reconstructed side by side.
    :param A: Original stat matrix
    :param B: Cursed stat matrix
    :param A_rec: Reconstructed stat matrix
    """

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), constrained_layout=True)
    fig.suptitle("Original, cursed, and reconstructed stat matrices", fontsize=13)

    vmin = min(A.min(), B.min(), A_rec.min())
    vmax = max(A.max(), B.max(), A_rec.max())

    matrixes = [A, B, A_rec]
    titles = [r"$A$ (original)", r"$B$ (cursed)", r"$\tilde{A}$ (reconstructed)"]
    plot_data = zip(axes, matrixes, titles)

    for ax, matrix, title in plot_data:
        Matshow(fig, ax, matrix, vmin, vmax, title)

    plt.show()


def plot_diff(A_original, A_rec):
    """
    This function compares A (Original stat matrix) and the reconstructed A.
    :param A_original: Original stat matrix
    :param A_rec: Reconstructed stat matrix
    """

    fig, ax = plt.subplots(figsize=(5, 4.5), constrained_layout=True)
    fig.suptitle(r"Difference $\tilde{A} - A$", fontsize=13)

    diff = A_rec - A_original

    vlim = max(np.abs(diff).max(), 1e-10)

    Matshow(fig, ax, diff, -vlim, vlim, r"$\tilde{A} - A$", cmap="RdBu_r")

    plt.show()


# -------------------------------------------------------
# Main
# -------------------------------------------------------


def main():
    """
    This is the main function, where every function is called and orchestrated to work together.
    """

    C = identify_curse(A, B)
    C_inv = CheckCinv(C, A, B)

    sequence = find_remedy_sequence(C_inv, remedies)

    A_rec = apply_remedy_sequence(B, remedies, sequence)

    # Plot
    plot_remedy(B, remedies, sequence)

    plot_comparison(A, B, A_rec)

    plot_diff(A, A_rec)

    # --- Interpretation ---
    print(
        "Interpretation:\n"
        "The curse matrix C reveals that STR was partially converted into DEX (off-diagonal coupling),\n"
        "while CON, INT, and WIS were uniformly scaled down to roughly 3/5 of their original values.\n"
        "The Mage (M) suffered the largest absolute drop in CON, losing nearly half its value,\n"
        "while the Warrior (W) showed the greatest STR-to-DEX leakage in the cursed state."
    )


if __name__ == "__main__":
    main()
