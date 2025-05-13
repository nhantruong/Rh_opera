import rhinoscriptsyntax as rs
import Rhino
import Rhino.Geometry as rg

def process_mesh():
    """
    Selects a Mesh, projects it onto the XY plane, QuadRemeshes it, and draws lines, cylinders, and labels.
    """

    # Select the mesh
    mesh_id = rs.GetObject("Select Mesh", rs.filter.mesh)
    if not mesh_id:
        print("No Mesh selected.")
        return

    # Get the Mesh object
    #mesh_object = Rhino.RhinoDoc.ActiveDoc.Objects.Find(mesh_id)
    mesh = rs.coercemesh(mesh_id)
    #mesh =rs.conver  mesh_object.Geometry.ToMesh()

    # Find the lowest point of the Mesh
    min_z = min(v.Z for v in mesh.Vertices)
    lowest_point = rg.Point3d(mesh.Vertices.Where(lambda v: v.Z == min_z).First())

    # Create the XY plane 200mm below the lowest point
    target_z = min_z - 200
    target_plane = rg.Plane(rg.Point3d(0, 0, target_z), rg.Vector3d(0, 0, 1))

    # Project the Mesh onto the XY plane
    projected_mesh = mesh.DuplicateMesh()
    xform = rg.Transform.PlanarProjection(target_plane)
    projected_mesh.Transform(xform)

    # Add the projected Mesh to Rhino
    projected_mesh_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(projected_mesh)

    # QuadRemesh the projected Mesh
    qr_params = rg.QuadRemeshParameters()
    qr_params.AdaptiveQuadCount = True
    qr_params.TargetQuadCount = 100  # You can adjust the LOD here
    qr_params.AdaptiveSize = 50
    qr_params.DetectHardEdges = True
    remeshed = rg.Mesh.QuadRemesh(projected_mesh, qr_params)

    # Add the QuadRemeshed Mesh to Rhino
    if remeshed:
        remeshed_mesh_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(remeshed)
    else:
        print("QuadRemesh failed.")
        return

    # Draw lines, cylinders, and labels
    draw_geometry_and_labels(remeshed, target_z)

def draw_geometry_and_labels(mesh, target_z):
    """
    Draws lines, cylinders, and labels for the Mesh.
    """

    for vertex in mesh.Vertices:
        # Draw line
        line_id = rs.AddLine(vertex, (vertex.X, vertex.Y, target_z))

        # Draw cylinder
        cylinder_base = rs.AddCircle((vertex.X, vertex.Y, target_z), 1)  # Radius of 1 unit
        cylinder = rs.ExtrudeCurveStraight(cylinder_base, (0, 0, 0), (0, 0, vertex.Z - target_z))
        rs.DeleteObject(cylinder_base)

        # Draw labels
        text = "X={:.2f}\nY={:.2f}\nZ={:.2f}".format(vertex.X, vertex.Y, vertex.Z)
        rs.AddText(text, vertex, height=5)  # Text height of 5 units

if __name__ == "__main__":
    process_mesh()