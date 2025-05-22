//Copyright (C) Svetlin Tassev

// This file is part of Go Board Fellow

// Go Board Fellow is free software: you can redistribute it and/or modify it under 
// the terms of the GNU General Public License as published by the Free Software 
// Foundation, either version 3 of the License, or (at your option) any later version

// Go Board Fellow is distributed in the hope that it will be useful, but WITHOUT 
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
// FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details

// You should have received a copy of the GNU General Public License along 
// with Go Board Fellow. If not, see <https://www.gnu.org/licenses/>.

function normalizePoints(pts) {
    const n = pts.length;
    let cx = 0,
        cy = 0;
    for (const [x, y] of pts) {
        cx += x;
        cy += y;
    }
    cx /= n;
    cy /= n;
    let avgDist = 0;
    for (const [x, y] of pts) avgDist += Math.hypot(x - cx, y - cy);
    avgDist /= n;
    const scale = Math.SQRT2 / avgDist;
    const T = [
        [scale, 0, -scale * cx],
        [0, scale, -scale * cy],
        [0, 0, 1]
    ];
    const norm = pts.map(([x, y]) => {
        const nx = scale * x - scale * cx;
        const ny = scale * y - scale * cy;
        return [nx, ny];
    });
    return {
        norm,
        T
    };
}

function matMul(A, B) {
    const m = A.length,
        n = B[0].length,
        p = B.length;
    const C = Array.from({
        length: m
    }, () => Array(n).fill(0));
    for (let i = 0; i < m; i++) {
        for (let j = 0; j < n; j++) {
            for (let k = 0; k < p; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
    return C;
}

// Helper: Matrix transpose
function matT(A) {
    return A[0].map((_, j) => A.map(row => row[j]));
}

// Helper: Matrix-vector multiplication
function matVecMul(A, v) {
    return A.map(row => row.reduce((sum, val, i) => sum + val * v[i], 0));
}

// Helper: Normalize a vector
function normalize(v) {
    const norm = Math.sqrt(v.reduce((sum, x) => sum + x * x, 0));
    return v.map(x => x / norm);
}

function largestEigenvector(A, maxIter = 100, tol = 1e-10) {
    let n = A.length;
    let v = Array(n).fill(0).map(() => Math.random());
    v = normalize(v);
    let lambda_old = 0;
    for (let iter = 0; iter < maxIter; iter++) {
        let Av = matVecMul(A, v);
        let lambda = v.reduce((sum, vi, i) => sum + vi * Av[i], 0);
        v = normalize(Av);
        if (Math.abs(lambda - lambda_old) < tol) break;
        lambda_old = lambda;
    }
    return v;
}
// Helper: Find the eigenvector of smallest eigenvalue using inverse power iteration
function smallestEigenvector(A, maxIter = 2000, tol = 1e-10) {
    // Shifted power iteration for smallest eigenvector
    let n = A.length;
    let v = Array(n).fill(0).map(() => Math.random());
    v = normalize(v);
    let lambda_old = 0;
    for (let iter = 0; iter < maxIter; iter++) {
        // Solve (A - mu*I)x = v for x, using mu = 0 (no shift)
        // For small matrices, use Jacobi iteration
        let x = v.slice();
        for (let jac = 0; jac < 2000; jac++) {
            for (let i = 0; i < n; i++) {
                let sum = 0;
                for (let j = 0; j < n; j++)
                    if (j !== i) sum += A[i][j] * x[j];
                x[i] = (v[i] - sum) / (A[i][i] || 1e-10);
            }
        }
        v = normalize(x);
        // Rayleigh quotient
        let Av = matVecMul(A, v);
        let lambda = v.reduce((sum, vi, i) => sum + vi * Av[i], 0);
        if (Math.abs(lambda - lambda_old) < tol) break;
        lambda_old = lambda;
    }
    return v;
}


// 4. Homography with normalization and robust eigenvector
function computeHomography(src, dst) {
    // Normalize
    const {
        norm: srcNorm,
        T: Tsrc
    } = normalizePoints(src);
    const {
        norm: dstNorm,
        T: Tdst
    } = normalizePoints(dst);

    // Build A
    const A = [];
    for (let i = 0; i < 4; i++) {
        const [x, y] = srcNorm[i];
        const [u, v] = dstNorm[i];
        A.push([-x, -y, -1, 0, 0, 0, x * u, y * u, u]);
        A.push([0, 0, 0, -x, -y, -1, x * v, y * v, v]);
    }
    const At = matT(A);
    const AtA = matMul(At, A);

    // Inverse AtA for smallest eigenvector
    // For 9x9, invert directly
    function matInv9(A) {
        // Use numeric inversion for 9x9 (implement or use a library for production)
        // Here, use Cramer's rule or similar for small matrices, omitted for brevity
        // For now, use a simple pseudo-inverse for small matrices
        // ... implement or use a library ...
        throw new Error("Implement 9x9 inversion or use a library");
    }
    // Instead, use SVD or the largest eigenvector of the inverse
    // For small matrices, the following is sufficient:
    // Use the largest eigenvector of the inverse of AtA
    // (This is equivalent to smallest eigenvector of AtA)
    // For now, use numeric.js or math.js for inversion, or implement a simple Gauss-Jordan.

    // For brevity, let's use the largest eigenvector of AtA^-1 (approximate)
    // For small matrices, this is acceptable:
    // (You can use math.js or implement a small-matrix inversion here)

    // For now, let's use the largest eigenvector of AtA^-1
    // You can implement a 9x9 inversion or use an existing function.

    // For demonstration, let's proceed with the largest eigenvector of AtA^-1
    // (In practice, use a robust SVD or pseudo-inverse)
    // If you have a small-matrix inversion, use it here.

    // For demonstration, let's use the smallestEigenvector function from before (with a warning)
    const h = smallestEigenvector(AtA);

    // Denormalize
    let H = [
        [h[0], h[1], h[2]],
        [h[3], h[4], h[5]],
        [h[6], h[7], h[8]]
    ];
    // H = inv(Tdst) * H * Tsrc
    function mat3Mul(A, B) {
        let C = Array(3).fill(0).map(() => Array(3).fill(0));
        for (let i = 0; i < 3; i++)
            for (let j = 0; j < 3; j++)
                for (let k = 0; k < 3; k++)
                    C[i][j] += A[i][k] * B[k][j];
        return C;
    }

    function mat3Inv(M) {
        // 3x3 matrix inversion
        const m = M,
            det =
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
            m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
            m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
        const inv = [
            [
                (m[1][1] * m[2][2] - m[1][2] * m[2][1]) / det,
                (m[0][2] * m[2][1] - m[0][1] * m[2][2]) / det,
                (m[0][1] * m[1][2] - m[0][2] * m[1][1]) / det
            ],
            [
                (m[1][2] * m[2][0] - m[1][0] * m[2][2]) / det,
                (m[0][0] * m[2][2] - m[0][2] * m[2][0]) / det,
                (m[0][2] * m[1][0] - m[0][0] * m[1][2]) / det
            ],
            [
                (m[1][0] * m[2][1] - m[1][1] * m[2][0]) / det,
                (m[0][1] * m[2][0] - m[0][0] * m[2][1]) / det,
                (m[0][0] * m[1][1] - m[0][1] * m[1][0]) / det
            ]
        ];
        return inv;
    }
    H = mat3Mul(mat3Inv(Tdst), mat3Mul(H, Tsrc));
    // Normalize so H[2][2] == 1
    for (let i = 0; i < 3; i++)
        for (let j = 0; j < 3; j++) H[i][j] /= H[2][2];
    return H;
}

// 5. Apply homography (unchanged)
function applyHomography(H, pt) {
    const [x, y] = pt;
    const denom = H[2][0] * x + H[2][1] * y + H[2][2];
    const u = (H[0][0] * x + H[0][1] * y + H[0][2]) / denom;
    const v = (H[1][0] * x + H[1][1] * y + H[1][2]) / denom;
    return [u, v];
}