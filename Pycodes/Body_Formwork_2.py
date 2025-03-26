import rhinoscriptsyntax as rs
import Rhino

class MeshProcessor:
    """
    A class to process mesh objects, including QuadRemeshing, 
    transformations, and geometry creation.
    """

    def __init__(self, mesh_id, lod):
        """
        Initializes the MeshProcessor with a mesh ID and level of detail (LOD).
        """
        self.mesh_id = mesh_id
        self.lod = lod
        self.origin = None
        self.offset_lowest = None

    def calculate_new_origin(self):
        """
        Calculates the new origin point based on the mesh vertices.
        """
        vertices = rs.MeshVertices(self.mesh_id)
        if not vertices:
            print("Could not retrieve vertices from Mesh!")
            return None

        self.origin = min(vertices, key=lambda pt: pt[0] + pt[2])
        return self.origin

    def create_working_plane(self):
        """
        Creates a 10x10m working plane at the offset_lowest Z coordinate.
        """
        plane_corners = [
            (self.offset_lowest[0] - 5.0, self.offset_lowest[1] - 5.0, self.offset_lowest[2]),
            (self.offset_lowest[0] + 5.0, self.offset_lowest[1] - 5.0, self.offset_lowest[2]),
            (self.offset_lowest[0] + 5.0, self.offset_lowest[1] + 5.0, self.offset_lowest[2]),
            (self.offset_lowest[0] - 5.0, self.offset_lowest[1] + 5.0, self.offset_lowest[2])
        ]
        working_plane = rs.AddSrfPt(plane_corners)
        if not working_plane:
            print("Failed to create working plane!")
            return None

        rs.ObjectName(working_plane, "10m x 10m Working Plane")
        return working_plane

    def align_mesh_to_xy_plane(self):
        """
        Aligns the mesh to the XY plane and moves it to the target Z coordinate.
        """
        new_mesh_id = rs.CopyObject(self.mesh_id)
        mesh_geo = rs.coercemesh(self.mesh_id)
        point_1_3d = Rhino.Geometry.Point3d(self.origin[0], self.origin[1], self.origin[2])
        mesh_point = mesh_geo.ClosestMeshPoint(point_1_3d, 0.0)
        normal = mesh_geo.NormalAt(mesh_point)
        target_z = self.offset_lowest[2] + 0.2
        target_plane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(self.origin[0], self.origin[1], target_z),
                                            Rhino.Geometry.Vector3d(0, 0, 1))
        source_plane = Rhino.Geometry.Plane(point_1_3d, normal)
        rs.OrientObject(new_mesh_id, 
                        [source_plane.Origin, source_plane.Origin + source_plane.Normal],
                        [target_plane.Origin, target_plane.Origin + target_plane.Normal])
        new_vertices = rs.MeshVertices(new_mesh_id)
        new_lowest_z = min(v[2] for v in new_vertices)
        translation = (0, 0, target_z - new_lowest_z)
        rs.MoveObject(new_mesh_id, translation)
        self.mesh_id = new_mesh_id
        print("New Mesh lowest Z: {:.2f} (should be {:.2f})".format(min(v[2] for v in rs.MeshVertices(new_mesh_id)), target_z))

    def quad_remesh_mesh(self):
        """
        QuadRemeshes the mesh with the specified LOD.
        """
        new_mesh_2 = rs.coercemesh(self.mesh_id, True)
        quad_mesh = self.quad_remesh_lod(new_mesh_2, self.lod)
        if not quad_mesh:
            print("Failed to QuadRemesh new Mesh!")
            return None

        self.mesh_id = quad_mesh if not isinstance(quad_mesh, list) else quad_mesh[0]

    def create_geometry_and_labels(self):
        """
        Creates geometry (lines, cylinders, spheres) and labels for the mesh.
        """
        points = rs.MeshVertices(self.mesh_id)
        if not points:
            print("Could not extract points from new Mesh!")
            return

        lowest = min(points, key=lambda pt: pt[2])
        print("New Mesh - Lowest point: ({:.2f}, {:.2f}, {:.2f})".format(lowest[0], lowest[1], lowest[2]))

        rs.EnableRedraw(False)
        for pt in points:
            start_point_new = (pt[0] - self.origin[0], pt[1] - self.origin[1], pt[2] - self.origin[2])
            end_point = (pt[0], pt[1], self.offset_lowest[2])
            end_point_new = (end_point[0] - self.origin[0], end_point[1] - self.origin[1], end_point[2] - self.origin[2])
            line_id = rs.AddLine(pt, end_point)
            curve_length = rs.CurveLength(line_id) if line_id else 0.0
            cylinder_radius = 0.01
            cylinder_height = pt[2] - end_point[2]
            cylinder_base = rs.AddCircle(end_point, cylinder_radius)
            cylinder = rs.ExtrudeCurveStraight(cylinder_base, (0, 0, 0), (0, 0, cylinder_height))
            rs.DeleteObject(cylinder_base)
            rs.AddSphere(pt, 0.01)
            large_cylinder_radius = 0.02
            large_cylinder_base = rs.AddCircle(end_point, large_cylinder_radius)
            large_cylinder = rs.ExtrudeCurveStraight(large_cylinder_base, (0, 0, 0), (0, 0, 0.08))
            rs.DeleteObject(large_cylinder_base)
            text = "X={:.2f}\nY={:.2f}\nZ={:.2f}\nH={:.2f}".format(
                start_point_new[0], start_point_new[1], start_point_new[2], curve_length)
            rs.AddText(text, end_point, height=0.06)
            
            # Add original coordinate label on the remeshed surface
            original_coord_text = "X={:.2f}\nY={:.2f}\nZ={:.2f}".format(pt[0], pt[1], pt[2])
            rs.AddText(original_coord_text, pt, height=0.06)

        rs.AddText("Z_min: {:.2f}".format(lowest[2]), lowest, height=0.06)
        rs.EnableRedraw(True)

    def create_solid_from_mesh(self):
        """
        Creates a solid from the mesh with a 3mm thickness.
        """
        thickness = 0.003
        solid_id = rs.MeshOffset(self.mesh_id, thickness)
        if not solid_id:
            print("Failed to create solid from mesh!")
            return None

        self.mesh_id = solid_id

    def quad_remesh_lod(self, mesh_id, lod):
        """
        QuadRemeshes a mesh with a specified level of detail (LOD).
        """
        qr_params = Rhino.Geometry.QuadRemeshParameters()
        qr_params.AdaptiveQuadCount = True
        qr_params.TargetQuadCount = lod
        qr_params.AdaptiveSize = 50
        qr_params.DetectHardEdges = True
        remeshed = Rhino.Geometry.Mesh.QuadRemesh(mesh_id, qr_params)
        return remeshed
        
    def create_geometry_and_labels_for_point_plane(self, input_point, input_plane):
        """
        Creates geometry and labels for a given point relative to a plane.
        
        Args:
            input_point: The point (list or tuple of coordinates) to process.
            input_plane: The plane (Rhino.Geometry.Plane) to compare against.
        """
        
        # Calculate the closest point on the plane
        closest_point = input_plane.ClosestPoint(Rhino.Geometry.Point3d(input_point))
        
        # Calculate the distance from the point to the plane
        distance = input_point.DistanceTo(closest_point)
        
        # Create a line from the input point to the closest point on the plane
        line_id = rs.AddLine(input_point, closest_point)
        
        # Create a sphere at the input point
        sphere_id = rs.AddSphere(input_point, 0.01)  # 10mm radius
        
        # Create a text label with the distance
        text_label = "Distance: {:.2f}".format(distance)
        text_id = rs.AddText(text_label, input_point, height=0.06)  # 60mm text height
        
        # Create a circle on the plane at the closest point
        circle_id = rs.AddCircle(closest_point, 0.02)  # 20mm radius
        
        # Extrude the circle to create a cylinder
        cylinder_id = rs.ExtrudeCurveStraight(circle_id, closest_point, input_point)
        
        # Clean up temporary geometry
        rs.DeleteObject(circle_id)
        
        # Optional: Add arrows to the line to indicate direction
        # (This requires more advanced RhinoCommon usage)
        
        print("Geometry and labels created for point relative to plane.")

# Main execution
if __name__ == "__main__":
    rs.EnableRedraw(False)
    original_mesh_id = rs.GetObject("Select a Mesh", rs.filter.mesh)
    lod = rs.GetInteger("LOD target: ", 50, 0, 100)
    if original_mesh_id:
        mesh_processor = MeshProcessor(original_mesh_id, lod)
        mesh_processor.offset_lowest = mesh_processor.calculate_new_origin()
        if mesh_processor.offset_lowest:
            mesh_processor.create_working_plane()
            mesh_processor.align_mesh_to_xy_plane()
            mesh_processor.quad_remesh_mesh()
            mesh_processor.create_geometry_and_labels()
            mesh_processor.create_solid_from_mesh()
    
    rs.EnableRedraw(True)
    
    print("Completed!")