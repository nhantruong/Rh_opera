import rhinoscriptsyntax as rs
obj1 = rs.GetObject("Select object 1")
obj2 = rs.GetObject("Select object 2")
pt1 = obj1
if obj:
    origin = rs.GetPoint("Origin point")
    if origin:
        rs.ScaleObject( obj, origin, (1,2,3), True )
