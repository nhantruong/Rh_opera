import rhinoscriptsyntax as rs
import Rhino.Geometry as rg

def draw_column_reinforcement():
    """
    Draws column reinforcement for a cylindrical object.
    """

    # Get the cylindrical object
    cylinder_id = rs.GetObject("Select a cylindrical object (surface or tube)", 8 + 16)
    if not cylinder_id:
        return

    cylinder = rs.coercegeometry(cylinder_id)

    # Get the height of the cylinder
    if isinstance(cylinder, rg.Surface):
        height = cylinder.GetBoundingBox(True).Max.Z - cylinder.GetBoundingBox(True).Min.Z
    elif isinstance(cylinder, rg.Extrusion):
        height = cylinder.GetBoundingBox(True).Max.Z - cylinder.GetBoundingBox(True).Min.Z
    else:
        print("Invalid object type.")
        return

    # Define reinforcement parameters
    reinforcement_radius = 50  # Radius of the reinforcement bars
    reinforcement_count = 8  # Number of reinforcement bars
    reinforcement_spacing = height / 5  # Spacing between reinforcement rings
    stirrup_radius = reinforcement_radius + 20 # Radius of the stirrups

    # Get the center point of the cylinder's bottom face
    if isinstance(cylinder, rg.Surface):
        bottom_center = cylinder.GetBoundingBox(True).Center
        bottom_center.Z = cylinder.GetBoundingBox(True).Min.Z
    elif isinstance(cylinder, rg.Extrusion):
        bottom_center = cylinder.GetBoundingBox(True).Center
        bottom_center.Z = cylinder.GetBoundingBox(True).Min.Z
    else:
        print("Invalid object type.")
        return

    # Draw reinforcement bars
    for i in range(reinforcement_count):
        angle = i * 360.0 / reinforcement_count
        point = bottom_center + rg.Point3d(stirrup_radius * rg.Math.Cos(rg.Math.ToRadians(angle)), stirrup_radius * rg.Math.Sin(rg.Math.ToRadians(angle)), 0)
        line = rg.LineCurve(point, point + rg.Vector3d(0, 0, height))
        rs.AddCurve(line)

    # Draw reinforcement rings (stirrups)
    ring_count = int(height / reinforcement_spacing) + 1
    for i in range(ring_count):
        ring_center = bottom_center + rg.Vector3d(0, 0, i * reinforcement_spacing)
        circle = rg.Circle(rg.Plane.WorldXY, ring_center, stirrup_radius)
        rs.AddCurve(circle)

draw_column_reinforcement()