import rhinoscriptsyntax as rs
import Rhino.Geometry as rg


def get_mesh(mesh_id):
    """Retrieves and validates the mesh object."""
    mesh = rs.coercemesh(mesh_id)
    if not mesh:
        print "Invalid mesh input."
        return
    print "get_mesh_OK"
    return mesh
def offset_mesh(mesh,distance=0.025):
    offset_mesh = rs.MeshOffset(mesh, distance)
    if not offset_mesh:
        print("Could not Offset Mesh")
        return
    print "Offset_mesh_Method_OK"
    return offset_mesh


def extract_boundary_curves(mesh):
    """Extracts the boundary curves from the mesh."""
    boundary_curves = rs.MeshOutline(mesh) #mesh.GetOutlines(rg.Plane.WorldXY)
    if not boundary_curves:
        print "Could not extract boundary curves from the mesh."
        return
    print "extract_boundary_curves_OK"
    return boundary_curves

def create_offset_curves(boundary_curves, offset_distance=25.0):
    """Creates offset curves from the boundary curves."""
    offset_curves = []
    for curve in boundary_curves:
        if isinstance(curve, rg.PolylineCurve):
            curve = rs.CurveToNurbsCurve(curve)
            if curve:
                curve = rg.Curve(curve)
        if isinstance(curve, rg.Curve):
            rebuilt_curve = curve.Rebuild(curve.PointCount / 2, 3, True)
            if rebuilt_curve:
                curve = rebuilt_curve
            offset_curves = rg.Curve.Offset(curve, rg.Plane.WorldXY, offset_distance, rs.UnitSystem(rs.UnitScale()), rg.CurveOffsetCornerStyle.Sharp)
            if offset_curves and len(offset_curves) > 0:
                offset_curves.append(offset_curves[0])
            else:
                simplified_curve = curve.Simplify(rg.CurveSimplifyStyle.All, rs.UnitSystem(rs.UnitScale()) * 0.1, 0, 0)
                if simplified_curve:
                    offset_curves = rg.Curve.Offset(simplified_curve, rg.Plane.WorldXY, offset_distance, rs.UnitSystem(rs.UnitScale()), rg.CurveOffsetCornerStyle.Sharp)
                    if offset_curves and len(offset_curves) > 0:
                        offset_curves.append(offset_curves[0])
    print "create_offset_curves_OK"
    return offset_curves

def generate_rebar_curves(offset_curves, spacing=150.0):
    """Generates rebar solids along the offset curves with specified spacing."""
    rebar_solids = []
    for curve in offset_curves:
        rebar_solids.append(curve) #add the initial offset curve.
        length = curve.GetLength()
        num_rebars = int(length / spacing)

        if num_rebars > 1:
            domain = curve.Domain
            for i in range(1, num_rebars):
                t = domain.Min + (i * spacing) / length * (domain.Max - domain.Min)
                point = curve.PointAt(t)
                tangent = curve.TangentAt(t)
                if tangent:
                    normal = rg.Vector3d.CrossProduct(tangent, rg.Vector3d.ZAxis)
                    normal.Unitize()
                    offset_point = point + normal * spacing
                    new_curves = rg.Curve.Offset(curve, rg.Plane.WorldXY, spacing * i, rs.UnitSystem(rs.UnitScale()), rg.CurveOffsetCornerStyle.Sharp)
                    if new_curves and len(new_curves)>0:
                        rebar_solids.append(new_curves[0])
    print "generate_rebar_curves_OK"
    return rebar_solids    


mesh_id = rs.GetObject("Select mesh", 32)
mesh = get_mesh(mesh_id)
offset_mesh = offset_mesh(mesh,0.025)
boundary_curves = extract_boundary_curves(offset_mesh)
#offset_curves = create_offset_curves(boundary_curves,25)
rebar_curves = generate_rebar_curves(boundary_curves,100)