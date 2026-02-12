import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/Layout";

export default function AdminUploadLayout({ children }) {
  return (
    <ProtectedRoute adminOnly>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}
