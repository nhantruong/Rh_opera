import rhinoscriptsyntax as rs
curs = []
endpt=[]
obj = rs.GetObjects("select: ")
for i in obj:
    if rs.IsCurve(i):          
          endpt.append(rs.CurveEndPoint(i))

print(endpt)