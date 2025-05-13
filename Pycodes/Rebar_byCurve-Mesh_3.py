# Python script for Rhino 7 (IronPython 2.7)
# Purpose: Project a curve, extrude a circle along curve_1, and array rebars along curve_2
import rhinoscriptsyntax as rs
import Rhino

class CurveProcessor:
    def __init__(self):
        # Default parameters (units in meters)
        self.radius = 0.005          # Radius = 5mm = 0.005m
        self.array_spacing = 0.1     # Array spacing = 100mm = 0.1m
        self.curve_id = None         # Selected curve ID for projection
        self.mesh_id = None          # Selected mesh ID
        self.curve_1 = None          # Projected curve ID
        self.curve_2 = None          # New curve for array
        self.circle_1 = None         # Circle at start of curve_1
        self.rebar_length = None     # Length of original Rebar_1

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

    def create_circle_and_extrude(self):
        """Create a perpendicular circle at the start of curve_1 and extrude it along the curve."""
        # Get the start point and tangent of curve_1
        start_point = rs.CurveStartPoint(self.curve_1)
        if not start_point:
            print("Could not determine start point of curve_1.")
            return False
        
        tangent = rs.CurveTangent(self.curve_1, 0.0)  # Tangent at start (t=0.0)
        if not tangent:
            tangent = (1, 0, 0)  # Fallback direction
        
        # Create a plane perpendicular to the tangent at the start point
        plane = rs.PlaneFromNormal(start_point, tangent)
        self.circle_1 = rs.AddCircle(plane, self.radius)
        if not self.circle_1:
            print("Failed to create Circle_1.")
            return False
        rs.ObjectName(self.circle_1, "Circle_1")
        
        # Extrude Circle_1 along curve_1 to create Rebar_1
        rebar_1 = rs.ExtrudeCurve(self.circle_1, self.curve_1)
        if rebar_1:
            rs.ObjectName(rebar_1, "Rebar_1")
            rs.CapPlanarHoles(rebar_1)  # Ensure it's a solid
            self.rebar_length = rs.CurveLength(self.curve_1)  # Store length of original rebar
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
        """Array rebars along curve_2 with equal distances of 100mm, following curve_2."""
        if not self.curve_2 or not self.rebar_length:
            print("Curve_2 or rebar length not defined for array.")
            return False
        
        # Get the length of curve_2
        curve_2_length = rs.CurveLength(self.curve_2)
        if not curve_2_length:
            print("Could not determine length of curve_2.")
            return False
        
        # Calculate the number of rebars based on 100mm (0.1m) spacing
        num_rebars = int(curve_2_length / self.array_spacing) + 1
        
        rs.EnableRedraw(False)
        # Array rebars along curve_2
        for i in range(num_rebars):
            t_start = i * self.array_spacing / curve_2_length  # Start parameter
            t_end = min((i * self.array_spacing + self.rebar_length) / curve_2_length, 1.0)  # End parameter, clamped to 1.0
            
            # Get start point and tangent for the circle
            start_point = rs.EvaluateCurve(self.curve_2, t_start)
            if not start_point:
                continue
            tangent = rs.CurveTangent(self.curve_2, t_start)
            if not tangent:
                tangent = (1, 0, 0)  # Fallback
            
            # Create a circle at the start point
            plane = rs.PlaneFromNormal(start_point, tangent)
            circle = rs.AddCircle(plane, self.radius)
            if not circle:
                continue
            
            # Trim curve_2 to create a segment for extrusion
            segment = rs.TrimCurve(self.curve_2, (t_start, t_end), delete_input=False)
            if not segment:
                rs.DeleteObject(circle)
                continue
            
            # Extrude the circle along the segment
            rebar_copy = rs.ExtrudeCurve(circle, segment)
            if rebar_copy:
                rs.ObjectName(rebar_copy, "Rebar_1_copy_{}".format(i))
                rs.CapPlanarHoles(rebar_copy)  # Ensure it's a solid
            
            # Clean up temporary objects
            rs.DeleteObject(circle)
            rs.DeleteObject(segment)
        rs.EnableRedraw(True)
        return True

    def run(self):
        """Execute the full workflow."""
        if not self.select_objects():
            return
        
        if not self.project_curve():
            return
        
        self.create_circle_and_extrude()
        
        if self.select_curve_for_array():
            self.array_rebar()
        
        print("Process completed. Created: curve_1, Circle_1, Rebar_1, and Rebar_1 copies along curve_2")

# Run the script
if __name__ == "__main__":
    processor = CurveProcessor()
    processor.run()