import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

#Quadremesh parameters
def QuadRemesh_LOD(mesh_id,lod):
    if not mesh_id:
        return
    mesh = rs.coercemesh(mesh_id)

    qr_params = Rhino.Geometry.QuadRemeshParameters()
    qr_params.AdaptiveQuadCount=True
    qr_params.TargetQuadCount = lod
    qr_params.AdaptiveSize = 50
    qr_params.DetectHardEdges=True
    #qr_params.SymmetryAxis = Rhino.Geometry.QuadRemeshSymmetryAxis.X | Rhino.Geometry.QuadRemeshSymmetryAxis.Y | Rhino.Geometry.QuadRemeshSymmetryAxis.Z
    
    remeshed = Rhino.Geometry.Mesh.QuadRemesh(mesh,qr_params)

    return remeshed



def create_midpoint_mesh():
    # Prompt user to select two meshes
    mesh1_id = rs.GetObject("Select first mesh", rs.filter.mesh)
    if not mesh1_id:
        print("No first mesh selected")
        return
    
    mesh2_id = rs.GetObject("Select second mesh", rs.filter.mesh)
    if not mesh2_id:
        print("No second mesh selected")
        return
    
    # Estimate a target face count based on average of both meshes
    face_count1 = rs.coercemesh(mesh1_id).Faces.Count
    face_count2 = rs.coercemesh(mesh2_id).Faces.Count
    target_face_count = int((face_count1 + face_count2) / 2)
    
    # Apply QuadRemesh to both meshes to get similar topology
    mesh1_quad = QuadRemesh_LOD(mesh1_id,target_face_count)
    mesh2_quad = QuadRemesh_LOD(mesh2_id,target_face_count)
    #mesh1_quad = rs.QuadRemesh(mesh1_id, target_face_count, adaptive_size=0)
    #mesh2_quad = rs.QuadRemesh(mesh2_id, target_face_count, adaptive_size=0)
    
    if not mesh1_quad or not mesh2_quad:
        print("QuadRemesh failed")
        return
    
    # Convert to Rhino mesh objects
    mesh1 = rs.coercemesh(mesh1_quad)
    mesh2 = rs.coercemesh(mesh2_quad)
    
    # Verify vertex counts match after QuadRemesh
    if mesh1.Vertices.Count != mesh2.Vertices.Count:
        print("Warning: Vertex counts don't match perfectly after QuadRemesh")
        return
    
    # Create new mesh for result
    new_mesh = Rhino.Geometry.Mesh()
    
    # Calculate midpoints between corresponding vertices
    midpoints = []
    for i in range(mesh1.Vertices.Count):
        v1 = mesh1.Vertices[i]
        v2 = mesh2.Vertices[i]
        mid_x = (v1.X + v2.X) / 2
        mid_y = (v1.Y + v2.Y) / 2
        mid_z = (v1.Z + v2.Z) / 2
        midpoints.append((mid_x, mid_y, mid_z))
        new_mesh.Vertices.Add(mid_x, mid_y, mid_z)
    
    # Copy face structure from one of the quadremeshed meshes
    new_mesh.Faces.AddFaces(mesh1.Faces)
    
    # Compute normals for proper display
    new_mesh.Normals.ComputeNormals()
    
    # Add the new mesh to the document
    sc.doc.Objects.AddMesh(new_mesh)
    
    # Clean up temporary QuadRemesh results
    #rs.DeleteObject(mesh1_quad)
    #rs.DeleteObject(mesh2_quad)
    
    # Refresh the view
    sc.doc.Views.Redraw()
    print("New mesh created from midpoints successfully")

# Run the function
if __name__ == "__main__":
    create_midpoint_mesh()