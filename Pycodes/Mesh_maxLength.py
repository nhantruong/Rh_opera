import rhinoscriptsyntax as rs
obj = rs.GetObject("Select a mesh", rs.filter.mesh)
#Kiem tra mesh co Close hay ko
def isClosed(obj):
    if rs.IsMeshClosed(obj):
        print "The mesh is closed."
    else:
        print "The mesh is not closed."
#Dem so luong Face cua Mesh
def MeshFaceCount(obj):
    print "Quad faces:", rs.MeshQuadCount(obj)
    print "Triangle faces:", rs.MeshTriangleCount(obj)
    print "Total faces:", rs.MeshFaceCount(obj)

    
def MeshOutline(obj):     
    rs.MeshOutline(obj)
    
#Mesh Area
def meshArea(obj):
    if obj:
        area_rc = rs.MeshArea(obj)
    if area_rc:
        print "Mesh area:", area_rc[1]

#Mesh faces => draw face on mesh
def meshFaces(obj,draw):
    faces = rs.MeshFaces(obj, False)
    if faces:
        rs.EnableRedraw(False)
        i = 0
        while( i<=len(faces)-1 ):
            face = faces[i], faces[i+1], faces[i+2], faces[i]
            if draw:
                rs.AddPolyline( face )
            i += 3
        rs.EnableRedraw(True)

#Convert Mesh to Nurb
def meshtoNurb(obj):
    if obj: rs.MeshToNurb(obj)


#project Commands:
isClosed(obj)
MeshFaceCount(obj)
meshArea(obj)
meshFaces(obj,False)
meshtoNurb(obj)