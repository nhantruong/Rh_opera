import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

class RebarGenerator:
    """Generates rebar curves around a mesh."""

    def __init__(self, mesh_id, offset_distance=25.0, spacing=150.0, rebar_diameter=10.0):
        """
        Initializes the RebarGenerator.

        Args:
            mesh_id: The GUID of the mesh object.
            offset_distance: The offset distance from the mesh border (in mm).
            spacing: The spacing between rebar curves (in mm).
            rebar_diameter: The diameter of the rebar in mm.
        """
        self.mesh_id = mesh_id
        self.offset_distance = offset_distance
        self.spacing = spacing
        self.rebar_diameter = rebar_diameter
        self.mesh = None
        self.boundary_curves = []
        self.offset_curves = []
        self.rebar_curves = []
        self.layer_name = "Rebar_D" + str(self.rebar_diameter)

    def get_mesh(self):
        """Retrieves and validates the mesh object."""
        self.mesh = rs.coercemesh(self.mesh_id)
        if not self.mesh:
            print "Invalid mesh input."
            return False
        return True

    def extract_boundary_curves(self):
        """Extracts the boundary curves from the mesh."""
        self.boundary_curves = self.mesh.GetOutlines(rg.Plane.WorldXY)
        if not self.boundary_curves:
            print "Could not extract boundary curves from the mesh."
            return False
        return True

    def create_offset_curves(self):
        """Creates offset curves from the boundary curves."""
        for curve in self.boundary_curves:
            if isinstance(curve, rg.PolylineCurve):
                curve = rs.CurveToNurbsCurve(curve) #converts to nurbs curve.
                if curve:
                    curve = rg.Curve(curve) #convert rs curve to rg curve.
            if isinstance(curve, rg.Curve):
                # Rebuild the curve for better offset results
                rebuilt_curve = curve.Rebuild(curve.PointCount / 2, 3, True) #adjust point count as needed.

                if rebuilt_curve:
                    curve = rebuilt_curve

                offset_curves = rg.Curve.Offset(curve, rg.Plane.WorldXY, self.offset_distance, rs.UnitSystem(rs.UnitScale()), rg.CurveOffsetCornerStyle.Sharp)

                if offset_curves and len(offset_curves) > 0:
                    self.offset_curves.append(offset_curves[0])
                else:
                    #if the offset failed, try again with a simplified curve.
                    simplified_curve = curve.Simplify(rg.CurveSimplifyStyle.All, rs.UnitSystem(rs.UnitScale()) * 0.1, 0, 0) #tolerance is important!
                    if simplified_curve:
                        offset_curves = rg.Curve.Offset(simplified_curve, rg.Plane.WorldXY, self.offset_distance, rs.UnitSystem(rs.UnitScale()), rg.CurveOffsetCornerStyle.Sharp)
                        if offset_curves and len(offset_curves) > 0:
                            self.offset_curves.append(offset_curves[0])
        return True
        
    def generate_rebar_curves(self):
        """Generates rebar curves along the offset curves with specified spacing."""
        for curve in self.offset_curves:
            self.rebar_curves.append(curve)
            length = curve.GetLength()
            num_rebars = int(length / self.spacing)

            if num_rebars > 1:
                domain = curve.Domain
                for i in range(1, num_rebars):
                    t = domain.Min + (i * self.spacing) / length * (domain.Max - domain.Min)
                    point = curve.PointAt(t)
                    tangent = curve.TangentAt(t)
                    if tangent:
                        normal = rg.Vector3d.CrossProduct(tangent, rg.Vector3d.ZAxis)
                        normal.Unitize()
                        offset_point = point + normal * self.spacing
                        new_curves = rg.Curve.Offset(curve, rg.Plane.WorldXY, self.spacing * i, rs.UnitSystem(rs.UnitScale()), rg.CurveOffsetCornerStyle.Sharp)
                        if new_curves and len(new_curves)>0:
                            self.rebar_curves.append(new_curves[0])
        return True


    def create_rebar_layer(self):
        """Creates the rebar layer if it doesn't exist."""
        if not rs.IsLayer(self.layer_name):
            rs.AddLayer(self.layer_name)
        return True

    def add_rebar_to_layer(self):
        """Adds the generated rebar curves to the layer."""
        for curve in self.rebar_curves:
            curve_id = rs.AddCurve(curve)
            if curve_id:
                rs.ObjectLayer(curve_id, self.layer_name)
        print "Rebar curves created on layer:", self.layer_name
        return True

    def run(self):
        """Executes the rebar generation process."""
        if not self.get_mesh():
            return
        if not self.extract_boundary_curves():
            return
        if not self.create_offset_curves():
            return
        if not self.generate_rebar_curves():
            return
        if not self.create_rebar_layer():
            return
        if not self.add_rebar_to_layer():
            return

# Example usage:
mesh_id = rs.GetObject("Select mesh", 32)
if mesh_id:
    rebar_generator = RebarGenerator(mesh_id)
    rebar_generator.run()