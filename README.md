# Hypermesh-Hole-Feature-Matcher
Automated 2D/3D mesh feature extraction and matching tool for HyperMesh. Detects circular holes from shell elements and cylindrical surfaces from solid elements, then groups them by axis alignment. Built on HyperMesh Python API + NumPy.
It automatically extracts geometric features (holes) from 2D/3D finite element meshes, including:
- Free surface detection
- Hole loop reconstruction
- Cylindrical feature recognition
- Coaxial hole grouping
- Automatic SET_GRID generation
- ### 1. Mesh Topology Processing
- Extract nodes and elements from HyperMesh model
- Reconstruct element faces (hexa / penta / tetra)
- Identify free faces using face frequency filtering
- ### 2. Surface Reconstruction
- Build adjacency graph based on shared edges
- Extract connected surface loops using region growing algorithm

### 3. Geometric Feature Recognition
- Detect circular features in 3D space
- Fit plane using SVD (PCA)
- Fit circle using least-squares method
- Compute:
  - Axis direction
  - Center position
  - Radius
  - Fitting error

### 4. Hole Classification
- Unified representation for:
  - 2D holes (planar loops)
  - 3D cylindrical holes (surface loops)
 
### 5. Feature Grouping
Group holes based on:
Axis parallelism
Distance between centerlines
Identify coaxial hole systems

### 6. HyperMesh Automation
Automatically generate SET_GRID cards
Assign grouped nodes into sets
Enable downstream CAE workflows

All features are stored in a unified data structure:

```python
@dataclass
class HoleFeature:
    loop_nodes: list
    center: np.ndarray
    axis: np.ndarray
    radius: float
    error: float
