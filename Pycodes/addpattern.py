import rhinoscriptsyntax as rs
import Rhino

def drawpattern(): 
    l1= rs.AddLine([0,0,0],[0,3,0])
    l2= rs.AddLine([0,3,0],[3,3,0])
    l3= rs.AddLine([3,3,0],[3,0,0])
    l4= rs.AddLine([0,0,0],[3,0,0])

    centerPt=rs.CurveMidPoint(rs.AddLine([0,0,0],[3,3,0]))
    circle = rs.AddCircle(centerPt,1.5)
    rectange = rs.JoinCurves([l1,l2,l3,l4])
    pattern = [rectange,circle]

def draw_Pattern_on_mesh(mesh_id):
    pt = rs.AddPoint(rs.MeshAreaCentroid(mesh_id))
    pt2=Rhino.Geometry.Point3d(rs.MeshAreaCentroid(mesh_id))
    point = rs.PointCoordinates(pt)
    
    bbox = rs.BoundingBox(mesh_id)
    if not bbox:
        print("BoundingBox Mesh Error!")
        return
    #centroid = Rhino.Geometry.Point3d(
    #    (bbox[0][0] + bbox[6][0]) / 2,  
    #    (bbox[0][1] + bbox[6][1]) / 2,  
    #   (bbox[0][2] + bbox[6][2]) / 2)
       
    
    #phap tuyen tai tam
    mesh_geo = rs.coercemesh(mesh_id)
    closest_point = mesh_geo.ClosestMeshPoint(pt2,0.0)
    normal = mesh_geo.NormalAt(closest_point)
    if not normal:
        print("Khong tinh duoc phap tuyen cua Mesh!")
        return
    
    #Tao MP tam va Phap tuyen
    #plane = Rhino.Geometry.Plane(centroid, normal)
    plane = Rhino.Geometry.Plane(pt2, normal)
    #Ve Rec
    rect_size = 3.0
    rect_points = [
        plane.PointAt(-rect_size / 2, -rect_size / 2),
        plane.PointAt(rect_size / 2, -rect_size / 2),
        plane.PointAt(rect_size / 2, rect_size / 2),
        plane.PointAt(-rect_size / 2, rect_size / 2)
    ]
    rect_curve = rs.AddPolyline(rect_points + [rect_points[0]])
    
    #ve Circle
    circle_radius = 0.95
    circle = rs.AddCircle(plane, circle_radius)
    addTexttoPoint(pt2)
    #chieu cac Curves len Mesh
    #curves = [rect_curve, circle] + [rs.AddPoint(pt) for pt in point_positions]
    curves = [rect_curve, circle]
    for curve in curves:
        if curve:
            projected_curve = rs.ProjectCurveToMesh(curve, mesh_id, normal)
            if projected_curve:
                rs.DeleteObject(curve)
            else:
                print("Loi khi chieu Curves len Mesh!") 


def transformPattertoMesh(pat,mesh):
    pt = rs.AddPoint(rs.MeshAreaCentroid(mesh))
    point = rs.PointCoordinates(pt)
    #rotate plan
    plane = rs.WorldXYPlane()
    #plane = rs.RotatePlane(plane, 45.0, [0,0,1])
    pattern = drawpattern()    
    xforms = rs.XformTranslation([point.X,point.Y,point.Z])
    rs.TransformObjects(pattern,xforms,False)
    

def addTexttoPoint(pt):
    point = rs.PointCoordinates(pt)
    text=['X:',point.X,'\nY:',point.Y,'\nZ:',point.Z]
    XYplan = rs.WorldXYPlane()
    Cpplan = rs.ViewCPlane()
    #rotate plan around Z axis
    plan2=rs.RotatePlane(XYplan,45.0,[0,0,1])
    ptPlan = rs.MovePlane(XYplan,pt)    
    rs.AddText(text,ptPlan)






def main():
    mesh = rs.GetObjects("Chon Mesh", rs.filter.mesh)
    #pt = rs.AddPoint(rs.MeshAreaCentroid(mesh_id))
    for mesh_id in mesh:
        if not mesh_id:
            print("Khong co Mesh!")
            return    
        rs.EnableRedraw(False) 
        print("Dang ve Pattern...")
        draw_Pattern_on_mesh(mesh_id)   
        rs.EnableRedraw(True)    
        print("Finishes!")

if __name__ == "__main__":
    main()