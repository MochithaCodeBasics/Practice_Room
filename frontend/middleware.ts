import { auth } from "@/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const { pathname } = req.nextUrl;

  // Inject auth header for API calls going to the NestJS backend
  // Skip NextAuth routes which are handled separately
  if (pathname.startsWith("/api/") && !pathname.startsWith("/api/auth/")) {
    const accessToken = req.auth?.accessToken;

    if (accessToken) {
      const requestHeaders = new Headers(req.headers);
      requestHeaders.set("Authorization", `Bearer ${accessToken}`);

      return NextResponse.next({
        request: {
          headers: requestHeaders,
        },
      });
    }
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/api/:path*"],
};
