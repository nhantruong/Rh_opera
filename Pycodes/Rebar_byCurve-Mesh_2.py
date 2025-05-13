# Python script for Rhino 7 (IronPython 2.7)
# Purpose: Project a curve, offset it, extrude a circle along curve_1 to create Rebar_1, and array it along curve_2
import rhinoscriptsyntax as rs
import Rhino

class CurveProcessor:
    def __init__(self):
        # Default parameters (units in meters)
        self.offset_distance = 0.1   # Offset distance = 100mm = 0.1m
        self.radius = 0.005          # Radius = 5mm = 0.005m
        self.array_spacing = 0.1     # Array spacing = 100mm = 0.1m
        self.curve_id = None         # Selected curve ID for projection
        self.mesh_id = None          # Selected mesh ID
        self.curve_1 = None          # Projected curve ID
        self.curve_2 = None          # New curve for array
        self.circle_1 = None         # Circle at end of curve_1

    def select_objects(self):
        """Prompt user to select a curve and a mesh for projection."""
        self.curve_id = rs.GetObject("Select a curve to project", rs.filter.curve)
        if not self.curve_id:
            print("No curve selected. Script aborted.")
            return False
        
        self.mesh_id = rs.GetObject("Select a mesh to project onto", rs.filter.mesh)
        if not self.mesh_id:
            print("No mesh selected. Script aborted.")
            return False
        return True

    def project_curve(self):
        """Project the selected curve onto the mesh."""
        projected_curves = rs.ProjectCurveToMesh(self.curve_id, self.mesh_id, (0, 0, 1))  # Project along Z-axis
        if not projected_curves:
            print("Projection failed. Check curve and mesh alignment.")
            return False
        
        self.curve_1 = projected_curves[0]  # Take the first projected curve
        rs.ObjectName(self.curve_1, "curve_1")
        return True

    def offset_curve(self):
        """Offset the projected curve to both sides with proper direction."""
        start_point = rs.CurveStartPoint(self.curve_1)
        if not start_point:
            print("Could not determine curve start point for offset.")
            return False
        
        # Determine the offset plane and direction
        if rs.IsCurvePlanar(self.curve_1):
            plane = rs.CurvePlane(self.curve_1)
            normal = plane.Normal
        else:
            plane = rs.WorldXYPlane()
            normal = (0, 0, 1)
        
        # Offset to one side
        offset_curve_1 = rs.OffsetCurve(self.curve_1, start_point, self.offset_distance, normal)
        if offset_curve_1:
            if isinstance(offset_curve_1, list):
                offset_curve_1 = offset_curve_1[0]
            rs.ObjectName(offset_curve_1, "curve_offset_positive")
        
        # Offset to the opposite side
        offset_curve_2 = rs.OffsetCurve(self.curve_1, start_point, -self.offset_distance, normal)
        if offset_curve_2:
            if isinstance(offset_curve_2, list):
                offset_curve_2 = offset_curve_2[0]
            rs.ObjectName(offset_curve_2, "curve_offset_negative")
        
        return offset_curve_1 is not None or offset_curve_2 is not None

    def create_circle_and_extrude(self):
        """Create a perpendicular circle at the end of curve_1 and extrude it along the curve."""
        # Get the end point and tangent of curve_1
        end_point = rs.CurveEndPoint(self.curve_1)
        if not end_point:
            print("Could not determine end point of curve_1.")
            return False
        
        tangent = rs.CurveTangent(self.curve_1, 1.0)  # Tangent at end (t=1.0)
        if not tangent:
            tangent = (1, 0, 0)  # Fallback direction
        
        # Create a plane perpendicular to the tangent at the end point
        plane = rs.PlaneFromNormal(end_point, tangent)
        self.circle_1 = rs.AddCircle(plane, self.radius)
        if not self.circle_1:
            print("Failed to create Circle_1.")
            return False
        rs.ObjectName(self.circle_1, "Circle_1")
        
        # Extrude Circle_1 along curve_1 to create Rebar_1
        rebar_1 = rs.ExtrudeCurve(self.circle_1, self.curve_1)
        if rebar_1:
            rs.ObjectName(rebar_1, "Rebar_1")
            # Ensure it's a solid by capping (if needed)
            rs.CapPlanarHoles(rebar_1)
            return True
        else:
            print("Extrusion failed.")
            return False

    def select_curve_for_array(self):
        """Prompt user to select a new curve for array."""
        self.curve_2 = rs.GetObject("Select a curve for Rebar_1 array (curve_2)", rs.filter.curve)
        if not self.curve_2:
            print("No curve selected for array. Skipping array step.")
            return False
        rs.ObjectName(self.curve_2, "curve_2")
        return True

    def array_rebar(self):
        """Array Rebar_1 along curve_2 with specified spacing."""
        # Find Rebar_1 (the extruded object)
        rebar_1 = rs.ObjectsByName("Rebar_1")
        if not rebar_1:
            print("Rebar_1 not found for array.")
            return False
        rebar_1 = rebar_1[0]  # Take the first object with this name
        
        # Get the length of curve_2
        curve_length = rs.CurveLength(self.curve_2)
        if not curve_length:
            print("Could not determine length of curve_2.")
            return False
        
        # Calculate the number of array instances
        num_instances = int(curve_length / self.array_spacing) + 1
        
        # Get the direction for arraying (tangent at start of curve_2)
        direction = rs.CurveTangent(self.curve_2, 0)
        if not direction:
            direction = (1, 0, 0)  # Fallback to X-axis
        
        # Array Rebar_1 along curve_2
        for i in range(1, num_instances):
            distance = i * self.array_spacing
            translation = [distance * coord for coord in direction]
            rebar_copy = rs.CopyObject(rebar_1, translation)
            if rebar_copy:
                rs.ObjectName(rebar_copy, "Rebar_1_array_{}".format(i))
        
        return True

    def run(self):
        """Execute the full workflow."""
        if not self.select_objects():
            return
        
        if not self.project_curve():
            return
        
        self.offset_curve()
        self.create_circle_and_extrude()
        
        if self.select_curve_for_array():
            self.array_rebar()
        
        print("Process completed. Created: curve_1, curve_offset_positive, curve_offset_negative, Circle_1, Rebar_1, and Rebar_1 array along curve_2")

# Run the script
if __name__ == "__main__":
    processor = CurveProcessor()
    processor.run()