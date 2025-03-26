import rhinoscriptsyntax as rs
import Rhino

# Step 1: User selects a mesh and names it "Mesh_1"
mesh_1 = rs.GetObject("Select a Mesh", rs.filter.mesh)
if not mesh_1:
    print("No mesh selected!")
    exit()
rs.ObjectName(mesh_1, "Mesh_1")

# Step 2: Copy Mesh_1 and name the copy "Mesh_2" at the same position
mesh_2 = rs.CopyObject(mesh_1)
if not mesh_2:
    print("Failed to copy Mesh_1!")
    exit()
rs.ObjectName(mesh_2, "Mesh_2")

# Step 3: Change the layer of Mesh_2 to "Coffa_inside"
layer_name = "Coffa_inside"
if not rs.IsLayer(layer_name):
    rs.AddLayer(layer_name)
rs.ObjectLayer(mesh_2, layer_name)

# Step 4: Rotate Mesh_2 to be parallel to the XY plane while preserving Point_1 and Point_2 positions
vertices = rs.MeshVertices(mesh_1)
if not vertices:
    print("Failed to retrieve vertices from Mesh_1!")
    exit()

# Define Point 1 (bottom-left corner: min X and min Z) and Point 2 (bottom-right corner: max X and min Z)
bottom_points = [pt for pt in vertices if abs(pt[2] - min(v[2] for v in vertices)) < 0.001]  # Points at lowest Z
point_1 = min(bottom_points, key=lambda pt: pt[0])  # Bottom-left: smallest X among bottom points
point_2 = max(bottom_points, key=lambda pt: pt[0])  # Bottom-right: largest X among bottom points

# Get the normal of Mesh_1 at Point 1 to determine its orientation
mesh_geo = rs.coercemesh(mesh_1)
point_1_3d = Rhino.Geometry.Point3d(point_1[0], point_1[1], point_1[2])
mesh_point = mesh_geo.ClosestMeshPoint(point_1_3d, 0.0)
if not mesh_point:
    print("Could not find closest point on Mesh_1!")
    exit()
normal = mesh_geo.NormalAt(mesh_point)
if not normal:
    print("Could not calculate normal at Point 1!")
    exit()

# Define the source plane (current orientation of Mesh_2) and target plane (XY plane)
source_plane = Rhino.Geometry.Plane(point_1_3d, normal)
target_plane = Rhino.Geometry.Plane(point_1_3d, Rhino.Geometry.Vector3d(0, 0, 1))  # XY plane (Z-axis up)

# Rotate Mesh_2 to align with the XY plane
rs.OrientObject(mesh_2, 
                [source_plane.Origin, source_plane.Origin + source_plane.Normal],
                [target_plane.Origin, target_plane.Origin + target_plane.Normal])

# Adjust Mesh_2 to preserve Point_2's position by translating it back
new_vertices = rs.MeshVertices(mesh_2)
if not new_vertices:
    print("Failed to retrieve vertices from Mesh_2 after rotation!")
    exit()
new_point_2 = new_vertices[bottom_points.index(point_2)]  # Point_2 after rotation
translation = [point_2[0] - new_point_2[0], point_2[1] - new_point_2[1], point_2[2] - new_point_2[2]]
rs.MoveObject(mesh_2, translation)

# Step 5: Perform QuadRemesh, extract points, draw cylinders, spheres, and elevation text
# QuadRemesh Mesh_2
rs.Command("-QuadRemesh TargetQuadCount 100 AdaptiveSize 50 PreserveSharpEdges Yes _SelID {} _Enter".format(mesh_2))
quad_mesh = rs.LastCreatedObjects()
if not quad_mesh:
    print("Failed to QuadRemesh Mesh_2!")
    exit()
mesh_2_quad = quad_mesh if not isinstance(quad_mesh, list) else quad_mesh[0]

# Extract points from the QuadRemeshed Mesh_2
points = rs.MeshVertices(mesh_2_quad)
if not points:
    print("Failed to extract points from Mesh_2!")
    exit()

# Define offset_lowest for elevation reference (200mm below Point 1)
offset_lowest = (point_1[0], point_1[1], point_1[2] - 0.2)

# Add points and draw geometry
for pt in points:
    rs.AddPoint(pt)
    end_point = (pt[0], pt[1], offset_lowest[2])  # End point at working plane level
    
    # Draw line and calculate length
    line_id = rs.AddLine(pt, end_point)
    curve_length = rs.CurveLength(line_id) if line_id else 0.0
    
    # Cylinder: 20mm diameter (0.02m)
    cylinder_radius = 0.01
    cylinder_height = pt[2] - end_point[2]
    cylinder_base = rs.AddCircle(end_point, cylinder_radius)
    cylinder = rs.ExtrudeCurveStraight(cylinder_base, (0, 0, 0), (0, 0, cylinder_height))
    rs.DeleteObject(cylinder_base)
    
    # Sphere: 20mm diameter at the top
    rs.AddSphere(pt, 0.01)
    
    # Larger cylinder: 40mm diameter, 80mm height at the base
    large_cylinder_radius = 0.02
    large_cylinder_base = rs.AddCircle(end_point, large_cylinder_radius)
    large_cylinder = rs.ExtrudeCurveStraight(large_cylinder_base, (0, 0, 0), (0, 0, 0.08))
    rs.DeleteObject(large_cylinder_base)
    
    # Text with relative coordinates to Point 1
    text = "X={:.2f}\nY={:.2f}\nZ={:.2f}\nH={:.2f}".format(
        pt[0] - point_1[0], pt[1] - point_1[1], pt[2] - point_1[2], curve_length)
    rs.AddText(text, end_point, height=0.06)

# Step 6: Add annotations for Point 1 and Point 2 with real project coordinates
text_point_1 = "Point 1 (Bottom-Left): ({:.2f}, {:.2f}, {:.2f})".format(point_1[0], point_1[1], point_1[2])
rs.AddText(text_point_1, point_1, height=0.06)

text_point_2 = "Point 2 (Bottom-Right): ({ characteristics:.2f}, {:.2f}, {:.2f})".format(point_2[0], point_2[1], point_2[2])
rs.AddText(text_point_2, point_2, height=0.06)

print("Completed!")