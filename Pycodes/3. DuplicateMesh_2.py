import rhinoscriptsyntax as rs
import Rhino

# Function to process the mesh and apply operations to the new horizontal Mesh
def process_mesh_and_create_offset():
    # 1. User selects a Mesh
    original_mesh_id = rs.GetObject("Select a Mesh", rs.filter.mesh)
    if not original_mesh_id:
        print("No Mesh selected!")
        return
    
    # 2. Find two points at the bottom edge and create a working plane
    vertices = rs.MeshVertices(original_mesh_id)
    if not vertices:
        print("Could not retrieve vertices from Mesh!")
        return
    
    lowest_point = min(vertices, key=lambda pt: pt[2])
    bottom_points = [pt for pt in vertices if abs(pt[2] - lowest_point[2]) < 0.001]
    
    filtered_points = [pt for pt in bottom_points if pt != lowest_point]
    if not filtered_points:
        print("Could not find a second point at the bottom edge!")
        return
    second_point = min(filtered_points,
                       key=lambda pt: (pt[0] - lowest_point[0])**2 + (pt[1] - lowest_point[1])**2)
    
    # Offset downward by 200mm (0.2m) from lowest point
    offset_lowest = (lowest_point[0], lowest_point[1], lowest_point[2] - 0.2)
    
    # Create a 5x5m working plane parallel to XY
    plane_corners = [
        (offset_lowest[0] - 2.5, offset_lowest[1] - 2.5, offset_lowest[2]),
        (offset_lowest[0] + 2.5, offset_lowest[1] - 2.5, offset_lowest[2]),
        (offset_lowest[0] + 2.5, offset_lowest[1] + 2.5, offset_lowest[2]),
        (offset_lowest[0] - 2.5, offset_lowest[1] + 2.5, offset_lowest[2])
    ]
    working_plane = rs.AddSrfPt(plane_corners)
    if not working_plane:
        print("Failed to create working plane!")
        return
    
    # 3. Duplicate the original Mesh, rotate it to XY plane, and position 200mm above working plane
    new_mesh_id = rs.CopyObject(original_mesh_id)
    
    # Calculate the normal of the original Mesh at its lowest point
    mesh_geo = rs.coercemesh(original_mesh_id)
    lowest_point_3d = Rhino.Geometry.Point3d(lowest_point[0], lowest_point[1], lowest_point[2])
    mesh_point = mesh_geo.ClosestMeshPoint(lowest_point_3d, 0.0)
    if not mesh_point:
        print("Could not find closest point on Mesh!")
        return
    normal = mesh_geo.NormalAt(mesh_point)
    if not normal:
        print("Could not calculate normal at lowest point!")
        return
    
    # Define the target XY plane (horizontal) at Z = offset_lowest[2] + 0.2
    target_z = offset_lowest[2] + 0.2
    target_plane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(lowest_point[0], lowest_point[1], target_z),
                                        Rhino.Geometry.Vector3d(0, 0, 1))
    
    # Rotate the new Mesh to align with XY plane
    source_plane = Rhino.Geometry.Plane(lowest_point_3d, normal)
    rs.OrientObject(new_mesh_id, 
                    [source_plane.Origin, source_plane.Origin + source_plane.Normal],
                    [target_plane.Origin, target_plane.Origin + target_plane.Normal])
    
    # Move the new Mesh to ensure its lowest point is at target_z
    new_vertices = rs.MeshVertices(new_mesh_id)
    if not new_vertices:
        print("Could not retrieve vertices from new Mesh!")
        return
    new_lowest_z = min(v[2] for v in new_vertices)
    translation = (0, 0, target_z - new_lowest_z)
    rs.MoveObject(new_mesh_id, translation)
    
    # Verify the new Mesh position
    new_vertices_after_move = rs.MeshVertices(new_mesh_id)
    final_lowest_z = min(v[2] for v in new_vertices_after_move)
    print("New Mesh lowest Z after move: {:.2f} (should be {:.2f})".format(final_lowest_z, target_z))
    
    # 4. Process the new Mesh: QuadRemesh, extract points, and create geometry
    # QuadRemesh the new Mesh
    rs.Command("-QuadRemesh TargetQuadCount 21 AdaptiveSize 50 _SelID {} _Enter".format(new_mesh_id))
    quad_mesh = rs.LastCreatedObjects()
    if not quad_mesh:
        print("Failed to QuadRemesh new Mesh!")
        return
    quad_mesh_id = quad_mesh if not isinstance(quad_mesh, list) else quad_mesh[0]
    rs.DeleteObject(new_mesh_id)  # Delete the intermediate new Mesh
    new_mesh_id = quad_mesh_id   # Update new_mesh_id to the QuadRemeshed version
    
    # Extract points from QuadRemeshed Mesh
    points = rs.MeshVertices(new_mesh_id)
    if not points:
        print("Could not extract points from new Mesh!")
        return
    
    # Add extracted points to the project
    for pt in points:
        rs.AddPoint(pt)
    
    # Find the lowest point
    lowest = min(points, key=lambda pt: pt[2])
    print("New Mesh - Lowest point: ({:.2f}, {:.2f}, {:.2f})".format(lowest[0], lowest[1], lowest[2]))
    
    # Create geometry for the new Mesh
    for pt in points:
        start_point = (pt[0], pt[1], pt[2])
        end_point = (pt[0], pt[1], offset_lowest[2])  # To working plane
        
        # Cylinder: 20mm diameter (0.02m), from point to working plane
        cylinder_radius = 0.01
        cylinder_height = start_point[2] - end_point[2]
        cylinder_base = rs.AddCircle((pt[0], pt[1], end_point[2]), cylinder_radius)
        cylinder = rs.ExtrudeCurveStraight(cylinder_base, (0, 0, 0), (0, 0, cylinder_height))
        rs.DeleteObject(cylinder_base)
        
        # Sphere: 20mm diameter at the top
        rs.AddSphere(start_point, 0.01)
        
        # Larger cylinder: 40mm diameter, 80mm height at working plane
        large_cylinder_radius = 0.02
        large_cylinder_base = rs.AddCircle(end_point, large_cylinder_radius)
        large_cylinder = rs.ExtrudeCurveStraight(large_cylinder_base, (0, 0, 0), (0, 0, 0.08))
        rs.DeleteObject(large_cylinder_base)
        
        # Add text with coordinates at the working plane
        text = "({:.2f}, {:.2f}, {:.2f})".format(pt[0], pt[1], pt[2])
        rs.AddText(text, end_point, height=0.1)
    
    # Label the lowest point
    rs.AddText("Z_min: {:.2f}".format(lowest[2]), lowest, height=0.1)
    
    # Label the working plane
    rs.AddText("Working Plane: Z = {:.2f}".format(offset_lowest[2]), offset_lowest, height=0.1)

# Run the script
if __name__ == "__main__":
    rs.EnableRedraw(False)  # Disable redraw for speed
    process_mesh_and_create_offset()
    rs.EnableRedraw(True)
    print("Completed!")