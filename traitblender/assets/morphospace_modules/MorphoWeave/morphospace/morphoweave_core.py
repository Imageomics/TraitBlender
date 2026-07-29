"""
MorphoWeave Model Library core (PCA + Local RBF), matching agporto/SlicerMorphoWeave.

Ported from the MorphoWeave / former ATLASViewer reference implementation:
  - Template-centered PCA: target = template_dense + sum_i (z_i * sqrt(lambda_i) * mode_i)
  - Local RBF: k=min(32, n_landmarks), Gaussian weights, h = 75th percentile k-th NN distance
  - LPS/RAS: dense landmarks and SSM in RAS; template PLY typically LPS on disk
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
from scipy.spatial import cKDTree

_MODEL_SUFFIXES = (".ply", ".vtk", ".vtp", ".stl", ".obj")


def resolve_database_paths(database_dir: str | Path) -> dict[str, Path]:
    """Resolve model, dense, sparse (optional), and ssm paths in a MorphoWeave Model Library / DATABASE folder."""
    root = Path(database_dir).expanduser().resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Database folder not found: {root}")

    manifest_path = root / "manifest.json"
    files: dict[str, str] = {}

    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid manifest.json in {root}") from e
        raw = manifest.get("files")
        if not isinstance(raw, dict):
            raise ValueError(f"manifest.json missing 'files' object: {manifest_path}")
        files = {str(k): str(v) for k, v in raw.items() if v}
    else:
        files = _discover_files_fallback(root)

    resolved: dict[str, Path] = {"database_dir": root}
    if manifest_path.is_file():
        resolved["manifest"] = manifest_path

    key_map = {
        "model": ("model", _MODEL_SUFFIXES),
        "dense": ("dense", (".mrk.json", ".json", ".fcsv")),
        "sparse": ("sparse", (".mrk.json", ".json", ".fcsv")),
        "ssm": ("ssm", (".npz",)),
    }

    for out_key, (manifest_key, suffixes) in key_map.items():
        rel = files.get(manifest_key, "")
        path = _resolve_member(root, rel, out_key, suffixes)
        if path is not None:
            resolved[out_key] = path

    required = ("model", "dense", "ssm")
    missing = [k for k in required if k not in resolved]
    if missing:
        raise FileNotFoundError(
            f"Database folder missing required file(s) {missing}: {root}\n"
            f"Found: {', '.join(p.name for p in resolved.values() if p != root and p.is_file())}"
        )

    for key in required:
        if not resolved[key].is_file():
            raise FileNotFoundError(f"Required file not found ({key}): {resolved[key]}")

    return resolved


def _resolve_member(
    root: Path,
    rel: str,
    role: str,
    suffixes: tuple[str, ...],
) -> Path | None:
    if rel:
        candidate = (root / rel).resolve()
        if candidate.is_file():
            return candidate
        if candidate.exists():
            return candidate
    return _find_by_role(root, role, suffixes)


def _find_by_role(root: Path, role: str, suffixes: tuple[str, ...]) -> Path | None:
    patterns: list[str] = []
    if role == "model":
        patterns = ["template_model.ply", "template_model.*", "*model*.ply"]
    elif role == "dense":
        patterns = [
            "dense_correspondences.mrk.json",
            "dense_correspondences.*",
            "*dense*corr*.mrk.json",
            "*dense*.mrk.json",
        ]
    elif role == "sparse":
        patterns = ["sparse_landmarks.mrk.json", "sparse_landmarks.*", "*sparse*.mrk.json"]
    elif role == "ssm":
        patterns = ["ssm_model.npz", "*.npz"]

    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        files = [p for p in matches if p.is_file()]
        if files:
            return files[0].resolve()
    return None


def _discover_files_fallback(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for role in ("model", "dense", "sparse", "ssm"):
        if role == "model":
            suffixes = _MODEL_SUFFIXES
        elif role == "ssm":
            suffixes = (".npz",)
        else:
            suffixes = (".mrk.json", ".json", ".fcsv")
        path = _find_by_role(root, role, suffixes)
        if path is not None:
            out[role] = path.name
    return out


def _resolve_file(source: str | Path | dict[str, Path], key: str) -> Path:
    if isinstance(source, dict):
        if key not in source:
            raise KeyError(f"paths dict missing {key!r}; run resolve_database_paths first")
        return Path(source[key])
    path = Path(source).expanduser().resolve()
    if path.is_dir():
        return resolve_database_paths(path)[key]
    return path


def load_dense_landmarks(
    source: str | Path | dict[str, Path],
    *,
    to_ras: bool = True,
) -> np.ndarray:
    markup_path = _resolve_file(source, "dense")
    if not markup_path.is_file():
        raise FileNotFoundError(f"Dense landmarks not found: {markup_path}")

    points, coord_system = _read_markup_points(markup_path)
    if points.shape[0] < 1:
        raise ValueError(f"No control points in dense landmarks: {markup_path}")
    if points.shape[1] != 3:
        raise ValueError(
            f"Expected 3 coordinates per point, got shape {points.shape}: {markup_path}"
        )

    if to_ras and coord_system == "LPS":
        points = _lps_to_ras(points)
    return points


def load_ssm(source: str | Path | dict[str, Path]) -> dict[str, np.ndarray | int]:
    npz_path = _resolve_file(source, "ssm")
    if not npz_path.is_file():
        raise FileNotFoundError(f"SSM not found: {npz_path}")

    data = np.load(npz_path, allow_pickle=False)
    for required in ("mean_shape", "modes", "eigenvalues"):
        if required not in data:
            raise KeyError(f"{npz_path} missing array {required!r}")

    mean_shape = np.asarray(data["mean_shape"], dtype=np.float64)
    modes = np.asarray(data["modes"], dtype=np.float64)
    eigenvalues = np.asarray(data["eigenvalues"], dtype=np.float64).ravel()

    if mean_shape.ndim != 2 or mean_shape.shape[1] != 3:
        raise ValueError(
            f"mean_shape must be (n_points, 3), got {mean_shape.shape} in {npz_path}"
        )
    n_points = int(mean_shape.shape[0])

    if modes.ndim != 3 or modes.shape[0] != n_points or modes.shape[1] != 3:
        raise ValueError(
            f"modes must be (n_points, 3, n_modes); got {modes.shape}, "
            f"expected ({n_points}, 3, ?) in {npz_path}"
        )
    n_modes = int(modes.shape[2])

    if eigenvalues.shape != (n_modes,):
        raise ValueError(
            f"eigenvalues must be ({n_modes},), got {eigenvalues.shape} in {npz_path}"
        )

    return {
        "mean_shape": mean_shape,
        "modes": modes,
        "eigenvalues": eigenvalues,
        "n_points": n_points,
        "n_modes": n_modes,
    }


def load_template_mesh(source: str | Path | dict[str, Path]):
    """Load template surface as vtk.vtkPolyData."""
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    model_path = _resolve_file(source, "model")
    if not model_path.is_file():
        raise FileNotFoundError(f"Template mesh not found: {model_path}")

    reader = _mesh_reader_for_suffix(model_path.suffix.lower())
    reader.SetFileName(str(model_path))
    reader.Update()

    poly = vtk.vtkPolyData()
    poly.ShallowCopy(reader.GetOutput())
    if poly.GetNumberOfPoints() < 1:
        raise RuntimeError(f"Mesh has no points: {model_path}")
    return poly


def mesh_point_array(poly) -> np.ndarray:
    from vtk.util.numpy_support import vtk_to_numpy

    pts = vtk_to_numpy(poly.GetPoints().GetData())
    return np.asarray(pts, dtype=np.float64)


def mesh_face_triangles(poly) -> list[tuple[int, int, int]]:
    from vtk.util.numpy_support import vtk_to_numpy

    polys = poly.GetPolys()
    if polys is None or polys.GetNumberOfCells() < 1:
        return []
    data = vtk_to_numpy(polys.GetData())
    faces: list[tuple[int, int, int]] = []
    i = 0
    while i < len(data):
        nv = int(data[i])
        idx = [int(data[i + 1 + j]) for j in range(nv)]
        if nv == 3:
            faces.append((idx[0], idx[1], idx[2]))
        elif nv > 3:
            v0 = idx[0]
            for j in range(1, nv - 1):
                faces.append((v0, idx[j], idx[j + 1]))
        i += nv + 1
    return faces


def ssm_std_devs(eigenvalues: np.ndarray) -> np.ndarray:
    return np.sqrt(np.maximum(np.asarray(eigenvalues, dtype=np.float64).ravel(), 0.0))


def morphoweave_pc_coefficients(
    sigma_weights: np.ndarray | Sequence[float],
    eigenvalues: np.ndarray,
) -> np.ndarray:
    z = np.asarray(sigma_weights, dtype=np.float64).ravel()
    ev = np.asarray(eigenvalues, dtype=np.float64).ravel()
    if z.shape != ev.shape:
        raise ValueError(
            f"sigma_weights length {z.shape[0]} != eigenvalues length {ev.shape[0]}"
        )
    return z * ssm_std_devs(ev)


def reconstruct_dense_target(
    template_dense: np.ndarray,
    modes: np.ndarray,
    eigenvalues: np.ndarray,
    sigma_weights: np.ndarray | Sequence[float],
) -> np.ndarray:
    """target = template_dense + sum_i (z_i * sqrt(lambda_i) * mode_i)"""
    template = np.asarray(template_dense, dtype=np.float64)
    modes_arr = np.asarray(modes, dtype=np.float64)
    ev = np.asarray(eigenvalues, dtype=np.float64).ravel()
    z = np.asarray(sigma_weights, dtype=np.float64).ravel()
    n_modes = int(modes_arr.shape[2])

    if z.shape[0] > n_modes:
        raise ValueError(f"sigma_weights length {z.shape[0]} > n_modes {n_modes}")

    k = min(z.shape[0], n_modes)
    if k == 0 or np.allclose(z[:k], 0.0):
        return template.copy()

    coeff = morphoweave_pc_coefficients(z[:k], ev[:k])
    agg = np.tensordot(modes_arr[..., :k], coeff, axes=(2, 0))
    return template + agg


@dataclass(frozen=True)
class LocalRBFDeformer:
    indices: np.ndarray
    weights: np.ndarray
    bandwidth: float
    k_neighbors: int


def precompute_local_rbf(
    mesh_vertices: np.ndarray,
    template_landmarks: np.ndarray,
    *,
    k_neighbors: int | None = None,
) -> LocalRBFDeformer:
    verts = np.asarray(mesh_vertices, dtype=np.float64)
    lm = np.asarray(template_landmarks, dtype=np.float64)
    n_lm = int(lm.shape[0])
    if n_lm < 1:
        raise ValueError("template_landmarks must contain at least one point")
    k = int(min(32, n_lm) if k_neighbors is None else min(k_neighbors, n_lm))

    tree = cKDTree(lm)
    try:
        dist, idx = tree.query(verts, k=k, workers=-1)
    except TypeError:
        dist, idx = tree.query(verts, k=k)

    if k == 1:
        dist = np.reshape(dist, (-1, 1))
        idx = np.reshape(idx, (-1, 1))

    h = float(np.percentile(dist[:, -1], 75)) + 1e-9
    w = np.exp(-(dist * dist) / (h * h))
    w /= w.sum(axis=1, keepdims=True)
    return LocalRBFDeformer(
        indices=np.asarray(idx, dtype=np.int64),
        weights=np.asarray(w, dtype=np.float64),
        bandwidth=h,
        k_neighbors=k,
    )


def deform_mesh_vertices_local_rbf(
    mesh_vertices: np.ndarray,
    template_landmarks: np.ndarray,
    target_landmarks: np.ndarray,
    deformer: LocalRBFDeformer,
) -> np.ndarray:
    v0 = np.asarray(mesh_vertices, dtype=np.float64)
    template = np.asarray(template_landmarks, dtype=np.float64)
    target = np.asarray(target_landmarks, dtype=np.float64)
    if template.shape != target.shape:
        raise ValueError(
            f"template_landmarks {template.shape} != target_landmarks {target.shape}"
        )

    delta_lm = target - template
    neighbor_deltas = delta_lm[deformer.indices]
    disp = np.sum(neighbor_deltas * deformer.weights[..., np.newaxis], axis=1)
    return v0 + disp


def deform_template_mesh_vertices(
    mesh,
    template_dense: np.ndarray,
    target_dense: np.ndarray,
    *,
    mesh_from_lps: bool = True,
    deformer: LocalRBFDeformer | None = None,
) -> np.ndarray:
    """
    Return deformed vertex positions in the same CRS as the template file on disk
    (LPS when mesh_from_lps is True).
    """
    verts = mesh_point_array(mesh)
    if mesh_from_lps:
        verts = _lps_to_ras(verts)
    template_ras = np.asarray(template_dense, dtype=np.float64)
    target_ras = np.asarray(target_dense, dtype=np.float64)

    rbf = deformer or precompute_local_rbf(verts, template_ras)
    verts_def_ras = deform_mesh_vertices_local_rbf(verts, template_ras, target_ras, rbf)

    if mesh_from_lps:
        verts_def = verts_def_ras.copy()
        verts_def[:, :2] *= -1.0
    else:
        verts_def = verts_def_ras

    return verts_def


def build_deformed_mesh_arrays(
    paths: dict[str, Path],
    sigma_weights: np.ndarray | Sequence[float],
    *,
    mesh_from_lps: bool = True,
) -> tuple[np.ndarray, list[tuple[int, int, int]]]:
    """Load database, apply PCA + Local RBF; return vertices and triangle faces."""
    mesh = load_template_mesh(paths)
    template_dense = load_dense_landmarks(paths, to_ras=True)
    ssm = load_ssm(paths)

    if int(template_dense.shape[0]) != int(ssm["n_points"]):
        raise ValueError(
            f"Dense landmark count {template_dense.shape[0]} != SSM rows {ssm['n_points']}"
        )

    target_dense = reconstruct_dense_target(
        template_dense,
        ssm["modes"],
        ssm["eigenvalues"],
        sigma_weights,
    )

    vertices = deform_template_mesh_vertices(
        mesh,
        template_dense,
        target_dense,
        mesh_from_lps=mesh_from_lps,
    )
    return vertices, mesh_face_triangles(mesh)


def _norm_coordinate_system(cs: str) -> str:
    s = str(cs).upper()
    if "LPS" in s or s == "0":
        return "LPS"
    if "RAS" in s or s == "1":
        return "RAS"
    return "RAS"


def _lps_to_ras(points: np.ndarray) -> np.ndarray:
    out = np.asarray(points, dtype=np.float64, copy=True)
    out[:, :2] *= -1.0
    return out


def _read_markup_points(path: Path) -> tuple[np.ndarray, str]:
    if path.suffix.lower() == ".fcsv":
        return _read_fcsv_points(path)

    data = json.loads(path.read_text(encoding="utf-8"))
    markup = (data.get("markups") or [{}])[0]
    coord_system = _norm_coordinate_system(markup.get("coordinateSystem", "RAS"))
    control_points = markup.get("controlPoints") or []
    if control_points and all("id" in cp for cp in control_points):
        try:
            control_points = sorted(control_points, key=lambda cp: int(cp["id"]))
        except (TypeError, ValueError):
            pass
    points = np.asarray(
        [cp["position"] for cp in control_points],
        dtype=np.float64,
    )
    return points, coord_system


def _read_fcsv_points(path: Path) -> tuple[np.ndarray, str]:
    coord_system = "RAS"
    rows: list[tuple[float, float, float]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            if "CoordinateSystem" in line:
                coord_system = _norm_coordinate_system(line.split("=", 1)[-1])
            continue
        parts = line.strip().split(",")
        if len(parts) >= 4:
            try:
                rows.append((float(parts[1]), float(parts[2]), float(parts[3])))
            except ValueError:
                continue
    return np.asarray(rows, dtype=np.float64), coord_system


def _mesh_reader_for_suffix(suffix: str):
    import vtk

    readers: dict[str, type] = {
        ".ply": vtk.vtkPLYReader,
        ".stl": vtk.vtkSTLReader,
        ".vtk": vtk.vtkPolyDataReader,
        ".vtp": vtk.vtkXMLPolyDataReader,
        ".obj": vtk.vtkOBJReader,
    }
    cls = readers.get(suffix)
    if cls is None:
        raise ValueError(
            f"Unsupported mesh extension {suffix!r}; "
            f"expected one of {sorted(readers)}"
        )
    return cls()
