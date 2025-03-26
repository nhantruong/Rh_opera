import rhinoscriptsyntax as rs
import Rhino
mesh_id = rs.GetObject("Chon mesh",rs.filter.mesh)
points_id = rs.GetObjects("Chon Points",rs.filter.point)

def autoRemesh(mesh_id):
    #tu dong Quadrenesh
    rs.Command("-QuadRemesh TargetQuadCount 21 AdaptiveSize 50 _SelID {} _Enter".format(mesh_id))
    quad_mesh = rs.LastCreatedObjects()
    quad_mesh_id = quad_mesh[0]
    #extractpoint
    points = rs.ExtractPoints(quad_mesh_id)
    return quad_mesh_id,points

def autoAddSupport(mesh_Offset,points):
      if not mesh_Offset: mesh_Offset = 0.5
      #
      points = [rs.PointCoordinates(pt_id) for pt_id in points_id]
      lowest_point = min(points, key=lambda pt: pt[2])    
      #
      offset_z = lowest_point[2] - mesh_Offset

      plane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0, 0, offset_z),
      Rhino.Geometry.Vector3d(0, 0, 1))
      #
      x_min = min(pt[0] for pt in points)
      x_max = max(pt[0] for pt in points)
      y_min = min(pt[1] for pt in points)
      y_max = max(pt[1] for pt in points)
      surface_corners = [x_min, y_min, offset_z),(x_max, y_min, offset_z),
      (x_max, y_max, offset_z),(x_min, y_max, offset_z)]
      offset_surface = rs.AddSrfPt(surface_corners)
      #
      rs.AddPlaneSurface(plane, 1, 1)
      rs.EnableRedraw(False)
      for i in range(len(points)):
          start_point = Rhino.Geometry.Point3d(points[i][0], points[i][1], points[i][2])
          end_point = Rhino.Geometry.Point3d(points[i][0], points[i][1], offset_z)
          line = rs.AddLine(start_point, end_point)
          text = "(Point_{},X:{:.2f}, Y:{:.2f}, Z:{:.2f}, HeightToTop:{:.2f})".format(i,end_point.X, end_point.Y, end_point.Z,rs.CurveLength(line) )
          rs.AddText(text, end_point, height=0.1)
      rs.EnableRedraw(True)

mesh_Offset = 0.5
points = [rs.PointCoordinates(pt_id) for pt_id in points_id]
lowest_point = min(points, key=lambda pt: pt[2])

offset_z = lowest_point[2] - mesh_Offset



plane = Rhino.Geometry.Plane(
    Rhino.Geometry.Point3d(0, 0, offset_z),
    Rhino.Geometry.Vector3d(0, 0, 1)         
    )

x_min = min(pt[0] for pt in points)
x_max = max(pt[0] for pt in points)
y_min = min(pt[1] for pt in points)
y_max = max(pt[1] for pt in points)

surface_corners = [
    (x_min, y_min, offset_z),
    (x_max, y_min, offset_z),
    (x_max, y_max, offset_z),
    (x_min, y_max, offset_z)
    ]
offset_surface = rs.AddSrfPt(surface_corners)

rs.AddPlaneSurface(plane, 1, 1)

rs.EnableRedraw(False) 

#for pt in points:
for i in range(len(points)):
    #start_point = Rhino.Geometry.Point3d(pt[0], pt[1], pt[2])  
    #end_point = Rhino.Geometry.Point3d(pt[0], pt[1], offset_z)
    start_point = Rhino.Geometry.Point3d(points[i][0], points[i][1], points[i][2])
    end_point = Rhino.Geometry.Point3d(points[i][0], points[i][1], offset_z)
    line = rs.AddLine(start_point, end_point)
    text = "(Point_{},X:{:.2f}, Y:{:.2f}, Z:{:.2f}, HeightToTop:{:.2f})".format(i,end_point.X, end_point.Y, end_point.Z,rs.CurveLength(line) )
    rs.AddText(text, end_point, height=0.1)    
    #rs.AddText("Offset Surface: Z = {:.2f}".format(x_min, y_min, offset_z), height=0.1)


rs.EnableRedraw(True) 