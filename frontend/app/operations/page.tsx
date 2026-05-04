import { Suspense } from "react";

import { OperationsPageClient } from "@/components/operations-page-client";

export default function OperationsPage() {
  return (
    <Suspense fallback={<OperationsPageClient />}>
      <OperationsPageClient />
    </Suspense>
  );
}
