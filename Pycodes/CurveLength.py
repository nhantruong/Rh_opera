import rhinoscriptsyntax as rs
curlength = []
obj = rs.GetObjects("select: ")
for i in obj:
    if rs.IsCurve(i):
        curlength.append(rs.CurveLength(i))
print(curlength)