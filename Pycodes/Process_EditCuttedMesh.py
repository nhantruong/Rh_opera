import rhinoscriptsyntax as rs
import Rhino

#Ham xu ly Sub-Segment
def process_sub_segment(mesh_id):
    # Bước 2: QuadRemesh với Target Quad Count = 500, Adaptive Size = 50%
    rs.Command(f"-QuadRemesh TargetQuadCount 500 AdaptiveSize 50 _SelID {mesh_id} _Enter")
    quad_mesh = rs.LastCreatedObjects()[0]  # Lấy mesh vừa tạo
    
    # Bước 3: Chuyển Mesh sang NURBS
    nurb_surface = rs.MeshToNurb(quad_mesh)
    if not nurb_surface:
        print(f"Không thể chuyển Mesh {mesh_id} sang NURBS")
        return
    
    # Bước 4: Lấy đường biên bằng DupBorder
    boundary = rs.DuplicateSurfaceBorder(nurb_surface)
    
    # Bước 5: Duplicate Mesh mới và xoay về mặt phẳng XY, bật Point của NURBS
    # Duplicate Mesh
    new_mesh = rs.CopyObject(quad_mesh)
    # Xoay về mặt phẳng XY (nằm ngang, Z=0)
    bbox = rs.BoundingBox(new_mesh)
    if bbox:
        base_point = bbox[0]  # Điểm thấp nhất của Mesh
        target_plane = rs.PlaneFromNormal((0, 0, 0), (0, 0, 1))  # Mặt phẳng XY
        rs.OrientObject(new_mesh, [base_point, (base_point[0], base_point[1], base_point[2] + 1)], 
                        [target_plane[0], (target_plane[0][0], target_plane[0][1], target_plane[0][2] + 1)])
        # Đặt Z=0 cho Mesh mới
        rs.MoveObject(new_mesh, (0, 0, -base_point[2]))
    
    # Bật Point của NURBS mới
    rs.ObjectShow(nurb_surface)
    rs.Command(f"-EditPtOn _SelID {nurb_surface} _Enter")
    control_points = rs.SurfacePoints(nurb_surface)
    
    # Bước 6: Ghi chú tọa độ với Z=0 làm chuẩn
    if control_points:
        for pt in control_points:
            # Tọa độ 2D (chiếu xuống Z=0)
            pt_2d = (pt.X, pt.Y, 0)
            # Ghi chú tọa độ gốc (X, Y, Z)
            text = f"({pt.X:.2f}, {pt.Y:.2f}, {pt.Z:.2f})"
            rs.AddText(text, pt_2d, height=0.1)
    
    # Xóa đối tượng tạm nếu cần
    # rs.DeleteObject(boundary)  # Uncomment nếu không cần đường biên

# Hàm chính: Chọn các tấm và xử lý
def main():
    # Bước 1: Chọn các tấm (Mesh)
    mesh_ids = rs.GetObjects("Chọn các tấm (Mesh)", rs.filter.mesh)
    if not mesh_ids:
        print("Không có tấm nào được chọn!")
        return
    
    rs.EnableRedraw(False)  # Tắt redraw để tăng tốc
    for mesh_id in mesh_ids:
        print(f"Đang xử lý tấm {mesh_id}...")
        process_sub_segment(mesh_id)
    rs.EnableRedraw(True)
    print("Hoàn thành!")

# Chạy script
if __name__ == "__main__":
    main()