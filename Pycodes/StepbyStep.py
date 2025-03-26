import rhinoscriptsyntax as rs
import Rhino

def editMesh(mesh_id):
    if not rs.IsMesh(mesh_id):
        print("Chon Mesh!")
        return
        
def drawPlane(line1,line2)

   print("Mesh dang chon: ",mesh_id)
   #tao duong bien dang cua Mesh
   border = rs.DuplicateMeshBorder(mesh_id)
   plane = Rhino.Geometry.Plane(
            Rhino.Geometry.Line. .Point3d(rs.Endpoint(line1), y_pos, centroid[2]),  # Diem Goc
            Rhino.Geometry.Vector3d(0, 1, 0)  # Huong vuong goc voi Y
        )
        planes_y.append(plane)
        # Add new Planes to project
        rs.AddPlaneSurface(plane, 10, 10)
   



# Ham chinh
def main():
    # Chon Mesh
    mesh_id = rs.GetObject("Chon Mesh de cat", rs.filter.mesh)
    if not mesh_id:
        print("Chon Mesh lai!")
        return
    
    rs.EnableRedraw(False)  # Tat redraw de tang toc do cat
    print("Dang cat Mesh...")
    editMesh(mesh_id)
    rs.EnableRedraw(True)
    print("Hoan Thanh!")

# Chay script
if __name__ == "__main__":
    main()