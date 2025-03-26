import rhinoscriptsyntax as rs

original_mesh_id = rs.GetObject("Select a Mesh", rs.filter.mesh)
new_mesh = rs.MeshOffset(original_mesh_id,0.003)