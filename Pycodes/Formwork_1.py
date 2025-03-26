import rhinoscriptsyntax as rs
import Rhino
mesh_id = rs.GetObject("Chon mesh",rs.filter.mesh)
#points_id = rs.GetObjects("Chon Points",rs.filter.point)

def autoRemesh(mesh_id):
    #tu dong Quadrenesh
    rs.Command("-QuadRemesh TargetQuadCount 21 AdaptiveSize 50 _SelID {} _Enter".format(mesh_id))
    quad_mesh = rs.LastCreatedObjects()    
    if not quad_mesh:
        print("QuadRemesh Error!")
        return
    if isinstance(quad_mesh, list):
        quad_mesh_id = quad_mesh[0]
    else:
        quad_mesh_id = quad_mesh
    #extractpoint
    #points = rs.ExtractPoints(quad_mesh_id)
    points = rs.MeshVertices(quad_mesh_id)
    return rs.AddPointCloud(points),quad_mesh_id

def autoAddSupport(mesh_Offset,points_id):
      if not mesh_Offset: mesh_Offset = 0.5
      #
      points = [rs.PointCoordinates(pt_id) for pt_id in points_id]
      lowest_point = min(points_id, key=lambda pt: pt[2])    
      #
      offset_z = lowest_point[2] - mesh_Offset

      plane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0, 0, offset_z),
      Rhino.Geometry.Vector3d(0, 0, 1))
      #
      x_min = min(pt[0] for pt in points)
      x_max = max(pt[0] for pt in points)
      y_min = min(pt[1] for pt in points)
      y_max = max(pt[1] for pt in points)
      surface_corners = [(x_min, y_min, offset_z),(x_max, y_min, offset_z),(x_max, y_max, offset_z),(x_min, y_max, offset_z)]
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
      
if __name__ == "__main__":
    rs.EnableRedraw(False)
    points_id = autoRemesh(mesh_id)[0]
    autoAddSupport(0.7,points_id)
    rs.EnableRedraw(True)
    print("Done nha!")