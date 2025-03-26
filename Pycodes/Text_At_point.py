import rhinoscriptsyntax as rs
import Rhino

def create_geometry_and_labels_for_point_plane(input_point, input_plane):
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


point = rs.GetObject("Select a Point", rs.filter.point)
plane = rs.GetObject("Select a Plane")

create_geometry_and_labels_for_point_plane(point,plane)