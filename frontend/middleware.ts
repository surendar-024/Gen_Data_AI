import { NextRequest, NextResponse } from "next/server";
import { verifyToken } from "@/lib/auth";

export async function middleware(request: NextRequest) {
  const token = request.cookies.get("gendataai_token")?.value;
  const { pathname } = request.nextUrl;

  // Protected routes — require authentication
  if (pathname.startsWith("/chat")) {
    if (!token) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
    const user = await verifyToken(token);
    if (!user) {
      const response = NextResponse.redirect(new URL("/login", request.url));
      response.cookies.delete("gendataai_token");
      return response;
    }
  }

  // Auth pages — redirect to chat if already logged in
  if (pathname === "/login" || pathname === "/register") {
    if (token) {
      const user = await verifyToken(token);
      if (user) {
        return NextResponse.redirect(new URL("/chat", request.url));
      }
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/chat/:path*", "/login", "/register"],
};
