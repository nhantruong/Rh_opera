import rhinoscriptsyntax as rs
#curs = rs.GetObjects('select Curves:')
curs = rs.GetObjects('select Curves:')
div = []
#endpt = rs.CurveEndPoint(rec)
#div = rs.DivideCurveLength(rec,2400,endpt,True)
stPt = rs.CurveStartPoint(curs)
div = rs.DivideCurveLength(curs,800,stPt,True)

#for cur in curs:
#    pt = rs.CurveStartPoint(cur)
#    if rs.IsPoint(pt):        
#        div.append(rs.AddPoints(pt))
print(div)