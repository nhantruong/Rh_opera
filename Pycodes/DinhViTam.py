import rhinoscriptsyntax as rs
import Rhino

#Ham Toi uu Mesh truoc khi cat


# Ham cat Mesh thanh cac tam 3m
def cut_mesh_into_plates(mesh_id):
    if not rs.IsMesh(mesh_id):
        print("Chon Mesh!")
        return
    
    # Tinh tam Mesh va BoundingBox
    bbox = rs.BoundingBox(mesh_id)
    if not bbox:
        print("Khong the tinh BoundingBox!")
        return
    centroid = ((bbox[0][0] + bbox[6][0]) / 2, 
              (bbox[0][1] + bbox[6][1]) / 2, 
              (bbox[0][2] + bbox[6][2]) / 2)  # Tam cua Mesh
    print("Centroid: ",centroid)
    #Xac dinh chieu dai cat theo x-Y
    length_x = bbox[6][0] - bbox[0][0] # Chieu dai theo phuong X    
    length_y = bbox[6][1] - bbox[0][1]  # Chieu dai theo phuong  Y
    print("Length X-Y: ",length_x,length_y)
    
    #So luong mat phang cat theo X-Y
    num_cuts_x = int(length_x / 3.0) + 1
    num_cuts_y = int(length_y / 3.0) + 1
    print("So luong MP cat X: ",num_cuts_x)
    print("So luong MP cat Y: ",num_cuts_y)
    # Danh sach MP cat
    planes_x = []
    planes_y = []
    
    # MP cat Doc theo X (vuong goc X)
    for i in range(-num_cuts_x // 2, num_cuts_x // 2 + 1):
        x_pos = centroid[0] + i * 3.0
        plane = Rhino.Geometry.Plane(
            Rhino.Geometry.Point3d(x_pos, centroid[1], centroid[2]),  # Diem Goc
            Rhino.Geometry.Vector3d(1, 0, 0)  # Huong vuong goc voi X
        )
        planes_x.append(plane)
        # Add new Planes to project
        rs.AddPlaneSurface(plane, 10, 10)  # Kich thuoc MP cat
    
    # MP cat Doc theo Y (vuong goc Y)
    for j in range(-num_cuts_y // 2, num_cuts_y // 2 + 1):
        y_pos = centroid[1] + j * 3.0
        plane = Rhino.Geometry.Plane(
            Rhino.Geometry.Point3d(centroid[0], y_pos, centroid[2]),  # Diem Goc
            Rhino.Geometry.Vector3d(0, 1, 0)  # Huong vuong goc voi Y
        )
        planes_y.append(plane)
        # Add new Planes to project
        rs.AddPlaneSurface(plane, 10, 10)
    
    # Chuyen Mesh thanh Rhino Geometry de cat
    mesh_geo = rs.coercemesh(mesh_id)
    if not mesh_geo:
        print("Khong the chuyen Mesh thanh Geometry!")
        return
    
    # Cat Mesh bang cac New planes
    mesh_fragments = [mesh_geo]
    for plane in planes_x + planes_y:
        new_fragments = []
        for fragment in mesh_fragments:
            split_meshes = Rhino.Geometry.Mesh.Split(fragment, plane)
            new_fragments.extend(split_meshes)
        mesh_fragments = new_fragments
    
    # Xoa Mesh Goc
    #rs.DeleteObject(mesh_id)
    #for fragment in mesh_fragments:
    #    rs.AddMesh(fragment.Vertices, fragment.Faces)
    





# Ham chinh
def main():
    # Chon Mesh
    mesh_id = rs.GetObject("Chon Mesh de cat", rs.filter.mesh)
    if not mesh_id:
        print("Chon Mesh lai!")
        return
    
    rs.EnableRedraw(False)  # Tat redraw de tang toc do cat
    print("Dang cat Mesh...")
    cut_mesh_into_plates(mesh_id)
    rs.EnableRedraw(True)
    print("Hoan Thanh!")

# Chay script
if __name__ == "__main__":
    main()