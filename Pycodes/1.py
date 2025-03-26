import rhinoscriptsyntax as rs
surf = rs.GetObject("Select surface for isocurve extraction", rs.filter.surface)
#frames = rs.GetObjects("Select frames")

border = []
border = rs.DuplicateSurfaceBorder(surf)
print(border)