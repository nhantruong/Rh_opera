import rhinoscriptsyntax as rs
obj = rs.GetObject("Select surface for isocurve extraction", rs.filter.surface)
point = rs.GetPointOnSurface(obj, "Select location for extraction")
parameter = rs.SurfaceClosestPoint(obj, point)
rs.ExtractIsoCurve( obj, parameter, 2 )
