import rhinoscriptsyntax as rs
def PrintControlPoints():
    surface = rs.GetObject("Select surface", rs.filter.surface)
    points = rs.SurfacePoints(surface)
    if points is None: return
    for i in points:
        np = rs.PointAdd(i)
    count = rs.SurfacePointCount(surface)
    i = 0
    for u in range(count[0]):
        for v in range(count[1]):
            print "CV[", u, ",", v, "] = ", points[i]
            i += 1
surface = rs.GetObject("Select surface", rs.filter.surface)
points = rs.SurfacePoints(surface)
for i in points:
    np = rs.AddPoint(i)
#PrintControlPoints()
