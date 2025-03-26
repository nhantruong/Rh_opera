import rhinoscriptsyntax as rs
import Rhino

# Function to process the original Mesh: QuadRemesh and extract points
def process_original_mesh(mesh_id, offset_lowest):
    # QuadRemesh the original Mesh
    rs.Command("-QuadRemesh TargetQuadCount 21 AdaptiveSize 50 _SelID {} _Enter".format(mesh_id))
    quad_mesh = rs.LastCreatedObjects()
    if not quad_mesh:
        print("Failed to QuadRemesh original Mesh!")
        return None
    quad_mesh_id = quad_mesh if not isinstance(quad_mesh, list) else quad_mesh[0]
    
    # Extract points from QuadRemeshed Mesh
    points = rs.MeshVertices(quad_mesh_id)
    if not points:
        print("Could not extract points from original Mesh!")
        return None
    
    # Add extracted points to the project
    for pt in points:
        rs.AddPoint(pt)
    
    # Find the lowest point
    lowest = min(points, key=lambda pt: pt[2])
    print("Original Mesh - Lowest point: ({:.2f}, {:.2f}, {:.2f})".format(lowest[0], lowest[1], lowest[2]))
    
    # Label the lowest point
    rs.AddText("Z_min: {:.2f}".format(lowest[2]), lowest, height=0.1)
    
    return quad_mesh_id

# Main function to process the mesh with geometry for the new Mesh
def process_mesh_with_geometry():
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
    
    # Find the four corner points based on convention
    lowest_z = min(pt[2] for pt in vertices)
    bottom_points = [pt for pt in vertices if abs(pt[2] - lowest_z) < 0.001]  # Bottom edge points
    top_points = [pt for pt in vertices if abs(pt[2] - lowest_z) > 0.001]     # Top edge points
    
    # Point 1: Bottom-left (min X among bottom points) as new origin [0,0,0]
    point_1 = min(bottom_points, key=lambda pt: pt[0])
    # Point 2: Bottom-right (max X among bottom points)
    point_2 = max(bottom_points, key=lambda pt: pt[0])
    # Point 4: Top-left (min X among top points)
    point_4 = min(top_points, key=lambda pt: pt[0])
    # Point 3: Top-right (max X among top points)
    point_3 = max(top_points, key=lambda pt: pt[0])
    
    # Define new coordinates relative to point_1 as origin [0,0,0]
    origin = point_1
    point_1_new = (point_1[0] - origin[0], point_1[1] - origin[1], point_1[2] - origin[2])
    point_2_new = (point_2[0] - origin[0], point_2[1] - origin[1], point_2[2] - origin[2])
    point_3_new = (point_3[0] - origin[0], point_3[1] - origin[1], point_3[2] - origin[2])
    point_4_new = (point_4[0] - origin[0], point_4[1] - origin[1], point_4[2] - origin[2])
    
    print("New Origin (Point 1): X={:.2f}, Y={:.2f}, Z={:.2f}".format(point_1_new[0], point_1_new[1], point_1_new[2]))
    print("Point 2 (Bottom-Right): X={:.2f}, Y={:.2f}, Z={:.2f}".format(point_2_new[0], point_2_new[1], point_2_new[2]))
    print("Point 3 (Top-Right): X={:.2f}, Y={:.2f}, Z={:.2f}".format(point_3_new[0], point_3_new[1], point_3_new[2]))
    print("Point 4 (Top-Left): X={:.2f}, Y={:.2f}, Z={:.2f}".format(point_4_new[0], point_4_new[1], point_4_new[2]))
    
    # Offset downward by 200mm (0.2m) from Point 1
    offset_lowest = (point_1[0], point_1[1], point_1[2] - 0.2)
    offset_lowest_new = (offset_lowest[0] - origin[0], offset_lowest[1] - origin[1], offset_lowest[2] - origin[2])
    
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
    
    # 3. Duplicate the original Mesh and position it 200mm above working plane
    new_mesh_id = rs.CopyObject(original_mesh_id)
    
    # Calculate the normal of the original Mesh at Point 1
    mesh_geo = rs.coercemesh(original_mesh_id)
    point_1_3d = Rhino.Geometry.Point3d(point_1[0], point_1[1], point_1[2])
    mesh_point = mesh_geo.ClosestMeshPoint(point_1_3d, 0.0)
    if not mesh_point:
        print("Could not find closest point on Mesh!")
        return
    normal = mesh_geo.NormalAt(mesh_point)
    if not normal:
        print("Could not calculate normal at lowest point!")
        return
    
    # Define the target XY plane (horizontal) at Z = offset_lowest[2] + 0.2
    target_z = offset_lowest[2] + 0.2
    target_plane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(point_1[0], point_1[1], target_z),
                                        Rhino.Geometry.Vector3d(0, 0, 1))
    
    # Rotate the new Mesh to align with XY plane
    source_plane = Rhino.Geometry.Plane(point_1_3d, normal)
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
    print("New Mesh lowest Z: {:.2f} (should be {:.2f})".format(final_lowest_z, target_z))
    
    # 4. Process the new Mesh: QuadRemesh, extract points, and create geometry
    # QuadRemesh the new Mesh
    rs.Command("-QuadRemesh TargetQuadCount 21 AdaptiveSize 50 _SelID {} _Enter".format(new_mesh_id))
    quad_mesh = rs.LastCreatedObjects()
    if not quad_mesh:
        print("Failed to QuadRemesh new Mesh!")
        return
    new_mesh_id_quad = quad_mesh if not isinstance(quad_mesh, list) else quad_mesh[0]
    
    # Delete the unprocessed new_mesh_id
    rs.DeleteObject(new_mesh_id)
    new_mesh_id = new_mesh_id_quad  # Update to the QuadRemeshed version
    
    # Process only the new Mesh
    meshes_to_process = [new_mesh_id]
    
    for idx, m_id in enumerate(meshes_to_process):
        # Extract points from QuadRemeshed Mesh
        points = rs.MeshVertices(m_id)
        if not points:
            print("Could not extract points from Mesh {}!".format(idx))
            continue
        
        # Add extracted points to the project
        for pt in points:
            rs.AddPoint(pt)
        
        # Find the lowest point
        lowest = min(points, key=lambda pt: pt[2])
        print("New Mesh - Lowest point: ({:.2f}, {:.2f}, {:.2f})".format(lowest[0], lowest[1], lowest[2]))
        
        # Create geometry for the new Mesh
        for pt in points:
            # Convert coordinates relative to new origin (Point 1)
            start_point_new = (pt[0] - origin[0], pt[1] - origin[1], pt[2] - origin[2])
            end_point = (pt[0], pt[1], offset_lowest[2])  # To working plane in original coordinates
            end_point_new = (end_point[0] - origin[0], end_point[1] - origin[1], end_point[2] - origin[2])
            
            line_id = rs.AddLine(pt, end_point)
            curve_length = rs.CurveLength(line_id) if line_id else 0.0
            
            # Cylinder: 20mm diameter (0.02m), from point to working plane
            cylinder_radius = 0.01
            cylinder_height = pt[2] - end_point[2]
            cylinder_base = rs.AddCircle(end_point, cylinder_radius)
            cylinder = rs.ExtrudeCurveStraight(cylinder_base, (0, 0, 0), (0, 0, cylinder_height))
            rs.DeleteObject(cylinder_base)
            
            # Sphere: 20mm diameter at the top
            rs.AddSphere(pt, 0.01)
            
            # Larger cylinder: 40mm diameter, 80mm height at working plane
            large_cylinder_radius = 0.02
            large_cylinder_base = rs.AddCircle(end_point, large_cylinder_radius)
            large_cylinder = rs.ExtrudeCurveStraight(large_cylinder_base, (0, 0, 0), (0, 0, 0.08))
            rs.DeleteObject(large_cylinder_base)
            
            # Updated text with new coordinates relative to Point 1
            text = "X={:.2f}, Y={:.2f}, Z={:.2f}, H={:.2f}".format(
                start_point_new[0], start_point_new[1], start_point_new[2], curve_length)
            rs.AddText(text, end_point, height=0.1)
        
        # Label the lowest point
        rs.AddText("Z_min: {:.2f}".format(lowest[2]), lowest, height=0.1)
    
    # 5. Process the original Mesh after the new Mesh
    processed_original_mesh_id = process_original_mesh(original_mesh_id, offset_lowest)
    if not processed_original_mesh_id:
        print("Failed to process original Mesh!")
    
    # Label the working plane
    rs.AddText("Working Plane: Z = {:.2f}".format(offset_lowest_new[2]), offset_lowest, height=0.1)

# Run the script
if __name__ == "__main__":
    rs.EnableRedraw(False)  # Disable redraw for speed
    process_mesh_with_geometry()
    rs.EnableRedraw(True)
    print("Completed!")