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
        Draws the projection lines.
        """
        for line in projection_lines:
            rs.AddLine(line.From, line.To)

    def create_projected_points(self, projected_points):
        """
        Creates points at the projected locations.
        """
        for point in projected_points:
            rs.AddPoint(point)

    def run(self):
        """
        Executes the entire projection process.
        """
        rs.EnableRedraw(False)
        quadremeshed_mesh = self.quadremesh_mesh1()
        projected_points, projection_lines = self.project_points_to_mesh2(quadremeshed_mesh)
        self.draw_projection_lines(projection_lines)
        self.create_projected_points(projected_points)
        rs.EnableRedraw(True)

# Get user input for mesh IDs
mesh1_id = rs.GetObject("Select Mesh 1", 32)
mesh2_id = rs.GetObject("Select Mesh 2", 32)

# Create an instance of the MeshProjection class and run the process
if mesh1_id and mesh2_id:
    projection = MeshProjection(mesh1_id, mesh2_id)
    projection.run()