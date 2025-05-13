import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

class MeshProjection:
    def __init__(self, mesh1_id, mesh2_id, lod=50):
        """
        Initializes the MeshProjection class with two mesh IDs and level of detail (lod).
        """
        self.mesh1_id = mesh1_id
        self.mesh2_id = mesh2_id
        self.lod = lod

    def quadremesh_mesh1(self):
        """
        Quadremeshes the first mesh with custom parameters.
        """
        mesh1 = rs.coercemesh(self.mesh1_id)
        qr_params = rg.QuadRemeshParameters()
        qr_params.AdaptiveQuadCount = True
        qr_params.TargetQuadCount = self.lod
        qr_params.AdaptiveSize = 50
        qr_params.DetectHardEdges = True
        quadremeshed_mesh = rg.Mesh.QuadRemesh(mesh1, qr_params)
        return quadremeshed_mesh

    def project_points_to_mesh2(self, quadremeshed_mesh):
        """
        Projects the vertices of the quadremeshed mesh onto the second mesh.
        """
        mesh2 = rs.coercemesh(self.mesh2_id)
        projected_points = []
        projection_lines = []

        for vertex in quadremeshed_mesh.Vertices:
            ray = rg.Line(vertex, mesh2.ClosestPoint(vertex))
            projected_point = mesh2.ClosestPoint(vertex)
            projected_points.append(projected_point)
            projection_lines.append(ray)

        return projected_points, projection_lines

    def draw_projection_lines(self, projection_lines):
        """
        Draws the projection lines and places the shortest ones in a layer.
        """
        rs.EnableRedraw(False)  # Disable redraw for performance

        # Create or get the "Shortest Distance" layer
        layer_name = "Shortest Distance"
        if not rs.IsLayer(layer_name):
            rs.AddLayer(layer_name)

        min_length = min(line.Length for line in projection_lines) if projection_lines else 0
        for line in projection_lines:
            if line.Length == min_length:
                rs.AddLine(line.From, line.To)  # Add shortest lines to the layer
            else:
                rs.AddLine(line.From, line.To)

        rs.EnableRedraw(True)  # Re-enable redraw

    def create_projected_points(self, projected_points):
        """
        Creates points at the projected locations.
        """
        for point in projected_points:
            rs.AddPoint(point)

    def create_midpoint_mesh(self, projection_lines):
        """
        Creates a mesh from the midpoints of the projection lines.
        """
        midpoints = [line.PointAt(0.5) for line in projection_lines]
        if len(midpoints) < 3:
            return  # Need at least 3 points to create a mesh

        mesh = rg.Mesh()
        for point in midpoints:
            mesh.Vertices.Add(point)

        # Basic triangulation (can be improved with more sophisticated algorithms)
        for i in range(len(midpoints) - 2):
            mesh.Faces.AddFace(0, i + 1, i + 2)

        rs.AddMesh(mesh)

    def run(self):
        """
        Executes the entire projection process.
        """
        quadremeshed_mesh = self.quadremesh_mesh1()
        projected_points, projection_lines = self.project_points_to_mesh2(quadremeshed_mesh)
        self.draw_projection_lines(projection_lines)
        self.create_projected_points(projected_points)
        self.create_midpoint_mesh(projection_lines)

# Get user input for mesh IDs
mesh1_id = rs.GetObject("Select Mesh 1", 32)
mesh2_id = rs.GetObject("Select Mesh 2", 32)

# Create an instance of the MeshProjection class and run the process
if mesh1_id and mesh2_id:
    projection = MeshProjection(mesh1_id, mesh2_id)
    projection.run()