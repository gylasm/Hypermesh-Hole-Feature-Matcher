# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 11:03:33 2026

@author: Administrator
"""

import hm
import hm.entities as ent

model = hm.Model()
props_shell = hm.Collection(model,ent.Property,'cardimage = PSHELL')

# nodes collection
node_col = hm.Collection(model, ent.Node)

nodes = {}
nodes_dict = {}

for n in node_col:
    nid = n.id
    coord = n.coordinates  
    nodes[nid] = coord
    nodes_dict[nid] = n

print("node count:", len(nodes))

elem_col = hm.Collection(model, ent.Element,props_shell)

elements = {}

for e in elem_col:
    eid = e.id
    conn = e.nodes   
    elements[eid] = [n.id for n in conn]

print("elem count:", len(elements))

from collections import defaultdict

edge_count = defaultdict(int)

def make_edge(a, b):
    return tuple(sorted((a, b)))   

for eid, conn in elements.items():

    n = len(conn)

    for i in range(n):
        n1 = conn[i]
        n2 = conn[(i + 1) % n]   

        edge = make_edge(n1, n2)
        edge_count[edge] += 1

print("total edges:", len(edge_count))

free_edges = [e for e, c in edge_count.items() if c == 1]

print("free edges:", len(free_edges))

graph = defaultdict(set)

for (n1, n2) in free_edges:
    graph[n1].add(n2)
    graph[n2].add(n1)

visited_edges = set()
loops = []

def make_edge(a, b):
    return tuple(sorted((a, b)))

for start_node in graph:

    for neighbor in graph[start_node]:

        edge = make_edge(start_node, neighbor)

        if edge in visited_edges:
            continue

        path = [start_node, neighbor]
        prev = start_node
        curr = neighbor

        while True:
            next_nodes = graph[curr] - {prev}

            if not next_nodes:
                break

            next_node = next_nodes.pop()

            path.append(next_node)

            prev, curr = curr, next_node

            if next_node == path[0]:
                loops.append(path)
                break

        
        for i in range(len(path)-1):
            visited_edges.add(make_edge(path[i], path[i+1]))
            

import numpy as np


def compute_centroid(loop, nodes):

    pts = []

    for n in loop:
        if n in nodes:
            pts.append(nodes[n])

    pts = np.array(pts)

    if pts.shape[0] == 0:
        raise ValueError("Empty loop or invalid nodes")

    if pts.ndim == 1:
        return pts  # 防止退化

    return np.mean(pts, axis=0)

def compute_radii(loop, nodes, center):
    radii = []

    for n in loop:
        p = np.array(nodes[n])
        r = np.linalg.norm(p - center)
        radii.append(r)

    return np.array(radii)

def radial_consistency(radii):

    return np.std(radii) / np.mean(radii)


from dataclasses import dataclass
@dataclass
class HoleFeature:
    loop_nodes: list
    center: np.ndarray
    axis: np.ndarray
    radius: float
    error: float
    
    

def is_circle_3d(loop, nodes, threshold=0.05):

    pts = []

    for n in loop:
        if n in nodes:
            pts.append(nodes[n])

    pts = np.array(pts)

    if pts.shape[0] < 3:
        return False, None, None

    centroid = np.mean(pts, axis=0)
    X = pts - centroid

    U, S, Vt = np.linalg.svd(X)

    t1 = Vt[0]
    t2 = Vt[1]
    normal = Vt[2]

    proj = []

    for p in pts:
        v = p - centroid
        proj.append([np.dot(v, t1), np.dot(v, t2)])

    proj = np.array(proj)

    x = proj[:, 0]
    y = proj[:, 1]

    A = np.column_stack([2*x, 2*y, np.ones(len(x))])
    b = x**2 + y**2

    params, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    a, b_c, c = params

    center_2d = np.array([a, b_c])

    dist = np.sqrt((x - a)**2 + (y - b_c)**2)

    error = np.std(dist) / np.mean(dist)

    center_3d = centroid + a * t1 + b_c * t2
    
    radius = np.linalg.norm(nodes[n]-centroid)

    return HoleFeature(
    loop_nodes=loop,
    center=center_3d,
    axis=normal,
    radius=radius,
    error=error
)

def is_parallel(a, b, tol=1e-2):

    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)

    return abs(np.dot(a, b)) > (1 - tol)


def point_line_distance(p, p0, direction):

    direction = direction / np.linalg.norm(direction)

    return np.linalg.norm(np.cross(p - p0, direction))

holes = []

for i, loop in enumerate(loops):

    res = is_circle_3d(loop, nodes, threshold=0.05)

    if res.error < 0.05:

        holes.append(res)

        print(f"Loop {i} is a hole")
    




def create_set_grid(model, name, node_ids, node_dict):

    set_obj = ent.Set(model)
    set_obj.cardimage = "SET_GRID"
    set_obj.name = name

    node_objs = [node_dict[nid] for nid in node_ids]

    set_obj.ids = node_objs

    return set_obj



props_solid = hm.Collection(model,ent.Property,'cardimage = PSOLID')
elem_3d = hm.Collection(model,ent.Element,props_solid)
e_penta = []
e_hexa = []
e_tetra = []
for e in elem_3d:
    if e.config == 206:
        e_penta.append(e)        
for e in elem_3d:
    if e.config == 208:
        e_hexa.append(e)        
for e in elem_3d:
    if e.config == 204:
        e_tetra.append(e)
        
hexa_elems = {}

for e in e_hexa:

    eid = e.id

    hexa_elems[eid] = [n.id for n in e.nodes]

faces = []

for e in e_hexa:

    nodesi = hexa_elems[e.id]   # list of 8 node IDs

    faces.append([nodesi[0], nodesi[1], nodesi[2], nodesi[3]])
    faces.append([nodesi[4], nodesi[5], nodesi[6], nodesi[7]])
    faces.append([nodesi[0], nodesi[1], nodesi[5], nodesi[4]])
    faces.append([nodesi[1], nodesi[2], nodesi[6], nodesi[5]])
    faces.append([nodesi[2], nodesi[3], nodesi[7], nodesi[6]])
    faces.append([nodesi[3], nodesi[0], nodesi[4], nodesi[7]])


penta_elems = {}
for e in e_penta:
    eid = e.id
    penta_elems[eid] = [n.id for n in e.nodes]
    
for e in e_penta:
    nodesi = penta_elems[e.id]
    faces.append([nodesi[0], nodesi[1], nodesi[2]])
    faces.append([nodesi[4], nodesi[5], nodesi[3]])
    faces.append([nodesi[0], nodesi[1], nodesi[3], nodesi[4]])
    faces.append([nodesi[1], nodesi[2], nodesi[4], nodesi[5]])
    faces.append([nodesi[2], nodesi[3], nodesi[0], nodesi[5]])
    
tetra_elems = {}
for e in e_tetra:
    eid = e.id
    tetra_elems[eid] = [n.id for n in e.nodes]
    

for e in e_tetra:
    nodesi = tetra_elems[e.id]
    faces.append([nodesi[0], nodesi[1], nodesi[2]])
    faces.append([nodesi[0], nodesi[1], nodesi[3]])
    faces.append([nodesi[2], nodesi[1], nodesi[3]])
    faces.append([nodesi[0], nodesi[2], nodesi[3]])
    
face_count = {}   
face_dict = {}

for f in faces:
    face_sorted = tuple(sorted(f))
    face_dict[face_sorted] = f
    face_count[face_sorted] = face_count.get(face_sorted,0)+1
   
free_faces = [f for f, c in face_count.items() if c == 1]
print(f"number of free faces of 3D-elements is: {len(free_faces)}")

face_edge_dict = {}


for f in free_faces:
    if len(face_dict[f]) == 3:
        edges_surface = []
        edges_surface.append(tuple(sorted([face_dict[f][0], face_dict[f][1]])))
        edges_surface.append(tuple(sorted([face_dict[f][1], face_dict[f][2]])))
        edges_surface.append(tuple(sorted([face_dict[f][2], face_dict[f][0]])))
        face_edge_dict[f] = edges_surface

    elif len(face_dict[f]) == 4:
        edges_surface = []
        edges_surface.append(tuple(sorted([face_dict[f][0], face_dict[f][1]])))
        edges_surface.append(tuple(sorted([face_dict[f][1], face_dict[f][2]])))
        edges_surface.append(tuple(sorted([face_dict[f][2], face_dict[f][3]])))
        edges_surface.append(tuple(sorted([face_dict[f][3], face_dict[f][0]])))
        face_edge_dict[f] = edges_surface



adj = defaultdict(list)

def share_edge(edges1, edges2):

    return len(set(edges1) & set(edges2)) > 0

keys = list(face_edge_dict.keys())

for i in range(len(keys)):
    for j in range(i+1, len(keys)):

        fi = face_edge_dict[keys[i]]
        fj = face_edge_dict[keys[j]]

        if share_edge(fi, fj):

            adj[keys[i]].append(keys[j])
            adj[keys[j]].append(keys[i])
            
visited = set()
components = []

for node in face_edge_dict.keys():

    if node in visited:
        continue

    stack = [node]
    comp = []

    while stack:

        cur = stack.pop()

        if cur in visited:
            continue

        visited.add(cur)
        comp.append(cur)

        for nb in adj[cur]:
            if nb not in visited:
                stack.append(nb)

    components.append(comp)           

print(f"There are {len(components)} 3D-elems Components")

def normal_tri(p1, p2, p3):

    v1 = p2 - p1
    v2 = p3 - p1

    n = np.cross(v1, v2)

    return n / np.linalg.norm(n)

def normal_quad(pts):

    n1 = normal_tri(pts[0], pts[1], pts[2])
    n2 = normal_tri(pts[0], pts[2], pts[3])

    n = n1 + n2

    return n / np.linalg.norm(n)

def face_nodes_coord(face,nodes):
    pts_coord = np.array([nodes[n] for n in face])
    return pts_coord

components_geom = []


global_faces_geom = {}

for comp in components:
    for nodes_key in comp:            
        nodes_ordered = face_dict[nodes_key]   
        pts = np.array([nodes[n] for n in nodes_ordered])

        if len(nodes_ordered) == 3:
            n = normal_tri(pts[0], pts[1], pts[2])
        elif len(nodes_ordered) == 4:
            n = normal_quad(pts)
        else:
            continue

        center = np.mean(pts, axis=0)

        global_faces_geom[nodes_key] = {
            "nodes": nodes_ordered,   # 原始顺序
            "pts": pts,
            "normal": n,
            "center": center
        }

print(f"Total free faces collected: {len(global_faces_geom)}")


adj = defaultdict(list)
face_keys = list(global_faces_geom.keys())

for i in range(len(face_keys)):
    for j in range(i + 1, len(face_keys)):
        key_i = face_keys[i]
        key_j = face_keys[j]
        edges_i = face_edge_dict[key_i]
        edges_j = face_edge_dict[key_j]

        if share_edge(edges_i, edges_j):
            adj[key_i].append(key_j)
            adj[key_j].append(key_i)


def region_growing(adj, geom_dict, tol=40):
    visited = set()
    surfaces = []

    for seed in geom_dict.keys():    # 现在 geom_dict 是字典，.keys() 正常
        if seed in visited:
            continue

        stack = [seed]
        surface = []

        while stack:
            cur = stack.pop()
            if cur in visited:
                continue

            visited.add(cur)
            surface.append(cur)

            for nb in adj[cur]:
                if nb not in visited:
                    n1 = geom_dict[cur]["normal"]
                    n2 = geom_dict[nb]["normal"]
                    if np.dot(n1, n2) > np.cos(np.radians(tol)):
                        stack.append(nb)

        surfaces.append(surface)

    return surfaces

surfaces = region_growing(adj, global_faces_geom, 40)

print(f"Total surfaces found: {len(surfaces)}")
single_face = [s for s in surfaces if len(s) == 1]
print(f"Surfaces with only 1 face: {len(single_face)}")

for i, surf in enumerate(surfaces):
    print(f"Surface {i}: {len(surf)} faces")

def fit_cylinder(points):
    """
    对点集拟合圆柱，返回 (axis, center_on_axis, radius, error)
    axis: 轴线单位向量
    center_on_axis: 轴线上一点（质心投影）
    radius: 拟合半径
    error: 半径标准差 / 半径均值
    """
    pts = np.array(points)
    if pts.shape[0] < 4:
        return None, None, None, 1e6

    # 1. PCA 估算轴线方向
    centroid = np.mean(pts, axis=0)
    cov = np.cov((pts - centroid).T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    axis = eigenvectors[:, 0]          # 最小特征值对应的方向（母线方向）

    # 2. 垂直于轴线的两个基向量
    if np.abs(axis[0]) < 0.9:
        ref = np.array([1, 0, 0])
    else:
        ref = np.array([0, 1, 0])
    t1 = np.cross(axis, ref)
    t1 /= np.linalg.norm(t1)
    t2 = np.cross(axis, t1)
    t2 /= np.linalg.norm(t2)

    # 3. 投影到 t1-t2 平面
    proj = np.array([[np.dot(p - centroid, t1), np.dot(p - centroid, t2)] for p in pts])
    x, y = proj[:, 0], proj[:, 1]

    # 4. 拟合 2D 圆
    A = np.column_stack([2*x, 2*y, np.ones_like(x)])
    b = x**2 + y**2
    params, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    a, b_c, c = params
    center_2d = np.array([a, b_c])
    radius = np.sqrt(c + a**2 + b_c**2)

    # 5. 3D 圆心（轴线上一点）
    center_3d = centroid + a * t1 + b_c * t2

    # 6. 计算误差
    distances = [np.linalg.norm(np.cross(p - center_3d, axis)) for p in pts]
    distances = np.array(distances)
    error = np.std(distances) / np.mean(distances) if np.mean(distances) > 0 else 1e6

    return axis, center_3d, radius, error


cylinder_holes = []   # 存放 HoleFeature 对象，与 holes 列表结构完全一致
threshold = 0.05      # 误差阈值，可调整

for i, surf in enumerate(surfaces):
    # 收集该表面所有节点ID（去重）和点坐标
    node_ids = set()
    all_points = []
    for face_key in surf:
        face_info = global_faces_geom[face_key]
        for nid in face_info["nodes"]:
            node_ids.add(nid)
        all_points.extend(face_info["pts"].tolist())

    if len(node_ids) < 5:
        continue

    axis, center, radius, error = fit_cylinder(all_points)

    if axis is not None and error < threshold:
        # 生成与2D孔洞完全一致的 HoleFeature 对象
        hole_feat = HoleFeature(
            loop_nodes=list(node_ids),   # 节点ID列表（无序）
            center=center,
            axis=axis,
            radius=radius,
            error=error
        )
        cylinder_holes.append(hole_feat)
        print(f"Surface {i} -> Cylinder HoleFeature: radius={radius:.2f}, error={error:.4f}, nodes={len(node_ids)}")
    else:
        print(f"Surface {i} is NOT a cylinder (error={error:.4f})")
        





holes = holes + cylinder_holes
print(f"Total features (2D + 3D): {len(holes)}")

groups = []

for h in holes:

    placed = False

    for g in groups:

        ref = g[0]

        if is_parallel(h.axis, ref.axis):

            d = point_line_distance(h.center, ref.center, ref.axis)

            if d < 0.1:

                g.append(h)
                placed = True
                break

    if not placed:
        groups.append([h])
        
all_sets=[]
pair_id = 1
for n in range(len(groups)):
    if len(groups[n]) == 1:
            continue
    for i in range(len(groups[n])):
        set_grid = create_set_grid(model,f"Pair_{int(pair_id)}_{int(i+1)}",groups[n][i].loop_nodes,nodes_dict) 
        all_sets.append(set_grid) 
        print(f"Set Pair{int(pair_id)}_{int(i+1)} is created")
    pair_id +=1





