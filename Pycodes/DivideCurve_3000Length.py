import rhinoscriptsyntax as rs

# Function to split a mesh into smaller meshes using curve division
def split_mesh_by_curves(mesh_id, segment_length=3.0):
    # Step 1: Duplicate the border of the mesh to get curves
    border_curves = rs.DuplicateMeshBorder(mesh_id)
    if not border_curves:
        print("Failed to duplicate mesh border!")
        return
    
    # Step 2: Identify Curve_1 (longest curve with lowest Z) and Curve_2 (highest Z)
    curve_data = []
    for curve in border_curves:
        # Get the curve length and Z-coordinate of its midpoint
        length = rs.CurveLength(curve)
        mid_point = rs.EvaluateCurve(curve, rs.CurveNormalizedParameter(curve, 0.5))
        z_value = mid_point[2]
        curve_data.append((curve, length, z_value))
    
    if not curve_data:
        print("No valid border curves found!")
        return
    
    # Find Curve_1: Longest curve among those with the lowest Z
    min_z = min(data[2] for data in curve_data)
    lowest_z_curves = [data for data in curve_data if abs(data[2] - min_z) < 0.001]
    curve_1_data = max(lowest_z_curves, key=lambda x: x[1])  # Longest curve at lowest Z
    curve_1 = curve_1_data[0]
    
    # Find Curve_2: Curve with the highest Z
    curve_2_data = max(curve_data, key=lambda x: x[2])  # Highest Z
    curve_2 = curve_2_data[0]
    
    print("Curve_1 length: {:.2f}m, Z: {:.2f}".format(curve_1_data[1], curve_1_data[2]))
    print("Curve_2 length: {:.2f}m, Z: {:.2f}".format(curve_2_data[1], curve_2_data[2]))
    
    # Step 3: Divide Curve_1 and Curve_2 into 3m segments
    curve_1_length = rs.CurveLength(curve_1)
    curve_2_length = rs.CurveLength(curve_2)
    num_divisions_1 = int(curve_1_length / segment_length) + 1
    num_divisions_2 = int(curve_2_length / segment_length) + 1
    num_divisions = min(num_divisions_1, num_divisions_2)  # Use the smaller number to ensure pairing
    
    # Divide curves into points
    curve_1_points = rs.DivideCurve(curve_1, num_divisions, create_points=False, return_points=True)
    curve_2_points = rs.DivideCurve(curve_2, num_divisions, create_points=False, return_points=True)
    
    if not curve_1_points or not curve_2_points:
        print("Failed to divide curves!")
        return
    
    # Step 4: Create closed polylines (4-sided) from divided points
    polylines = []
    for i in range(num_divisions - 1):
        # Define 4 points for a closed polyline
        pt1 = curve_1_points[i]      # Bottom-left
        pt2 = curve_1_points[i + 1]  # Bottom-right
        pt3 = curve_2_points[i + 1]  # Top-right
        pt4 = curve_2_points[i]      # Top-left
        
        # Create a closed polyline
        polyline = rs.AddPolyline([pt1, pt2, pt3, pt4, pt1])  # Add pt1 again to close it
        if polyline:
            polylines.append(polyline)
        else:
            print("Failed to create polyline at segment {}".format(i + 1))
    
    # Step 5: Create meshes from closed polylines
    meshes = []
    for i, polyline in enumerate(polylines):
        # Create a mesh from the polyline (simple planar mesh)
        mesh = rs.AddPlanarMesh(polyline)
        if mesh:
            rs.ObjectName(mesh, "Mesh_Segment_{}".format(i + 1))
            meshes.append(mesh)
        else:
            print("Failed to create mesh from polyline at segment {}".format(i + 1))
        rs.DeleteObject(polyline)  # Clean up the polyline after meshing
    
    # Clean up original border curves
    for curve in border_curves:
        rs.DeleteObject(curve)
    
    print("Successfully created {} mesh segments!".format(len(meshes)))
    return meshes

# Main script
if __name__ == "__main__":
    # User selects the mesh
    mesh_id = rs.GetObject("Select a mesh to split", rs.filter.mesh)
    if not mesh_id:
        print("No mesh selected!")
        exit()
    
    # Split the mesh into 3m segments based on curves
    segment_length = 3.0  # Length of each segment in meters
    split_mesh_by_curves(mesh_id, segment_length)
    
    print("Completed!")