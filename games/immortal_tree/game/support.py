from csv import reader
from os import walk, path as osp
import pygame


# ---------------------------------------------------------------------------
# CSV / folder helpers (carried over from the world_map reference)
# ---------------------------------------------------------------------------

def _resolve_asset_path(path):
    """Resolve asset paths relative to this module when given a relative path."""
    if osp.isabs(path):
        return path
    base_dir = osp.dirname(osp.abspath(__file__))
    return osp.normpath(osp.join(base_dir, path))

def import_csv_layout(path):
    """
    Read a CSV file and return a 2-D list of strings.

    Each cell value is a tile-ID string (e.g. '0', '42', '-1').
    '-1' conventionally means "empty / no tile".

    Args:
        path (str): Path to the CSV file.

    Returns:
        list[list[str]]: 2-D list where result[row][col] is the tile ID string.
    """
    terrain_map = []
    with open(_resolve_asset_path(path)) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
    return terrain_map


def import_folder(path):
    """
    Load every image file in *path* as a pygame Surface.

    Args:
        path (str): Directory containing image files (.png / .jpg / etc.).

    Returns:
        list[pygame.Surface]: Surfaces in filesystem order.
    """
    surface_list = []
    resolved_path = _resolve_asset_path(path)
    for _, __, img_files in walk(resolved_path):
        for image in sorted(img_files):          # sort for determinism
            full_path = resolved_path + '/' + image
            try:
                image_surf = pygame.image.load(full_path).convert_alpha()
                surface_list.append(image_surf)
            except Exception:
                pass                             # skip non-image files silently
    return surface_list


# ---------------------------------------------------------------------------
# NEW in Lab 6: sparse-matrix loader
# ---------------------------------------------------------------------------

def import_csv_to_sparse(path):
    """
    Load a CSV map layer into a SparseMatrix.

    Only non-(-1) cells are stored; the matrix therefore stays sparse even
    for large maps that are mostly empty.

    If the student has not yet implemented SparseMatrix (or it raises
    NotImplementedError), this function falls back to a plain dict with
    the same ``{(row, col): tile_id}`` interface so the rest of the game
    continues to work.

    Args:
        path (str): Path to the CSV file.

    Returns:
        SparseMatrix | dict: Mapping (row, col) -> int tile_id for every
            non-empty cell.  Both types expose ``.items()`` so the caller
            can iterate uniformly.
    """
    try:
        from datastructures.sparse_matrix import SparseMatrix
        matrix = SparseMatrix(default=-1)
        layout = import_csv_layout(path)
        for row_idx, row in enumerate(layout):
            for col_idx, val in enumerate(row):
                if val.strip() != '-1':
                    matrix.set(row_idx, col_idx, int(val.strip()))
        return matrix
    except Exception:
        # Graceful fallback — plain dict has the same .items() interface.
        result = {}
        layout = import_csv_layout(path)
        for row_idx, row in enumerate(layout):
            for col_idx, val in enumerate(row):
                if val.strip() != '-1':
                    result[(row_idx, col_idx)] = int(val.strip())
        return result
