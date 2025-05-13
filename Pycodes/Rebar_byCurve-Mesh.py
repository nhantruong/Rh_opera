# Python script for Rhino 7
# This script selects a curve and a mesh, projects the curve onto the mesh,
# names the projected curve as 'curve_1', and then offsets it to both sides by 100mm.
# Python version used in Rhino 7 is likely 2.7.

import rhinoscriptsyntax as rs

def project_and_offset_curve_on_mesh():
    """
    Selects a curve and a mesh, projects the curve onto the mesh,
    names the projected curve, and offsets it to both sides.
    """
    # Select a curve
    curve_id = rs.GetObject("Select a curve to project", filter=4)
    if not curve_id:
        print("No curve selected.")
        return

    # Select a mesh
    mesh_id = rs.GetObject("Select a mesh to project onto", filter=32)
    if not mesh_id:
        print("No mesh selected.")
        return

    # Project the curve onto the mesh
    projection_direction = (0, 0, -1) # Project along the negative Z-axis (adjust if needed)
    #projected_curve_ids = rs.ProjectCurveToSurface(curve_id, mesh_id, projection_direction)
    projected_curve_ids = rs.ProjectCurveToMesh(curve_id, mesh_id, projection_direction)

    if not projected_curve_ids:
        print("Curve projection failed.")
        return

    # Assuming only one curve was projected
    projected_curve_id = projected_curve_ids[0]

    # Name the projected curve
    rs.ObjectName(projected_curve_id, "curve_1")
    print("Projected curve named 'curve_1'.")

    # Offset the projected curve on the mesh
    offset_distance = 100.0 # mm

    # Offset to one side
    offset_curve_1_id = rs.OffsetCurveOnSurface(projected_curve_id, mesh_id, offset_distance)
    if offset_curve_1_id:
        rs.ObjectName(offset_curve_1_id, "curve_offset_1")
        print("Offset curve 1 created.")
    else:
        print("Offset curve 1 creation failed.")

    # Offset to the other side
    offset_curve_2_id = rs.OffsetCurveOnSurface(projected_curve_id, mesh_id, -offset_distance)
    if offset_curve_2_id:
        rs.ObjectName(offset_curve_2_id, "curve_offset_2")
        print("Offset curve 2 created.")
    else:
        print("Offset curve 2 creation failed.")

if __name__ == "__main__":
    project_and_offset_curve_on_mesh()