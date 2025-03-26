import rhinoscriptsyntax as rs
import Rhino

# 
def split_mesh_to_grid(mesh_id):
    # 
    if not rs.IsMesh(mesh_id):
        print("Chon Mesh!")
        return
    
    # 
    nurb_surface = rs.MeshToNurb(mesh_id)
    if not nurb_surface:
        print("Khong chuyen Mesh sang NURBS Surface!")
        return
    
    
    domain_u = rs.SurfaceDomain(nurb_surface, 0)  #  U
    domain_v = rs.SurfaceDomain(nurb_surface, 1)  #  V
    
    
    u_steps = 5
    v_steps = 5
    u_step_size = (domain_u[1] - domain_u[0]) / u_steps
    v_step_size = (domain_v[1] - domain_v[0]) / v_steps
    
    
    points = []
    
    
    for i in range(u_steps + 1):
        for j in range(v_steps + 1):
            u = domain_u[0] + i * u_step_size
            v = domain_v[0] + j * v_step_size
            point = rs.EvaluateSurface(nurb_surface, u, v)
            if point:
                points.append(point)                
                text = "point.X:" + point.X + "point.Y:" + point.Y + "point.Z:" + point.Z 
                rs.AddText(text, point, height=0.1)
    
    
    boundary = rs.DuplicateMeshBorder(mesh_id)
    if boundary:
        edge_points = rs.CurvePoints(boundary)
        for edge_point in edge_points:            
            #text = f"({edge_point.X:.2f}, {edge_point.Y:.2f}, {edge_point.Z:.2f})"
            text = "edge_point.X:" + point.X + "point.Y:" + point.Y + "edge_point.Z:" + edge_point.Z 
            rs.AddText(text, edge_point, height=0.1)
        rs.DeleteObject(boundary)  
    
    
    for i in range(u_steps + 1):
        u = domain_u[0] + i * u_step_size
        curve_v = rs.AddCurve([rs.EvaluateSurface(nurb_surface, u, v) for v in 
                               [domain_v[0] + j * v_step_size for j in range(v_steps + 1)]])
    for j in range(v_steps + 1):
        v = domain_v[0] + j * v_step_size
        curve_u = rs.AddCurve([rs.EvaluateSurface(nurb_surface, u, v) for u in 
                               [domain_u[0] + i * u_step_size for i in range(u_steps + 1)]])
    
    
    #rs.DeleteObject(nurb_surface)


def main():

    mesh_id = rs.GetObject("Chon Mesh")
    if not mesh_id:
        print("Khong co Mesh!")
        return
    
    rs.EnableRedraw(False) 
    print("Dang chia Mesh va gan Toa do...")
    split_mesh_to_grid(mesh_id)
    rs.EnableRedraw(True)
    print("Finishes!")

# script
if __name__ == "__main__":
    main()