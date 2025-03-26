import rhinoscriptsyntax as rs
import Rhino as rh
surf = rs.GetObject('Select Surface: ')
rh.Geometry.Surface.PointAt(surf,5,23)