import rhinoscriptsyntax as rs
curs = rs.GetObjects("Select a curve")

def dwgSpt(object):
    if rs.IsCurve(object):
        point = rs.CurveStartPoint(object)
        rs.AddPoint(point)

for i in range(len(curs)):
    if rs.IsCurve(curs[i]):
        dwgSpt(curs[i])
