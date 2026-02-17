import ProtectedRoute from "@/components/ProtectedRoute";
import Layout from "@/components/Layout";

export default function AdminUploadLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute adminOnly>
      <Layout>{children}</Layout>
    </ProtectedRoute>
  );
}
