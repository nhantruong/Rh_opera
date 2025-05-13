def export_mesh(self):
        """
        Exports the mesh to a file.
        """
        file_path = rs.SaveFileName("Export Mesh", "OBJ Files (*.obj)|*.obj|STL Files (*.stl)|*.stl||")
        if not file_path:
            return

        mesh = rs.coercemesh(self.mesh_id)
        if not mesh:
            print("Invalid mesh.")
            return

        file_extension = System.IO.Path.GetExtension(file_path).lower()
        if file_extension == ".obj":
            mesh.Write(file_path, rg.MeshWriteTopology.WriteOnlyQuads)
            print("Mesh exported to OBJ.")
        elif file_extension == ".stl":
            mesh.Write(file_path, rg.MeshWriteTopology.WriteOnlyTriangles)
            print("Mesh exported to STL.")
        else:
            print("Unsupported file format.")