import rhinoscriptsyntax as rs
rec = rs.GetObject('select rectangular')
startPt = rs.GetPointOnCurve(rec,'select basepoint')
mainframes = rs.GetObjects('Select mainframes')
pts=[]

reclist=[]
#Get startpoint of each frame
for frame in mainframes:
    if rs.IsCurve(frame):          
          pts.append(rs.CurveStartPoint(frame))
#Copy rectangular to 
for pt in pts:
    translation = pt-startPt
    reclist.append(rs.CopyObjects(rec,translation))

#loft to Solid

