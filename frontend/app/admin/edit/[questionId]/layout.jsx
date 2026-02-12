import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/Layout";

export default function AdminEditLayout({ children }) {
  return (
    <ProtectedRoute adminOnly>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}
