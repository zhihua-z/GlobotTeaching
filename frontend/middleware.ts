import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const studentPaths = [
  "/home",
  "/chat",
  "/practice",
  "/review",
  "/mistakes",
  "/progress",
  "/dashboard",
  "/legal-articles",
  "/questions",
  "/profile",
];

function isStudentPath(path: string): boolean {
  return studentPaths.some((p) => path.startsWith(p));
}

function hasSession(req: NextRequest): boolean {
  const token = req.cookies.get("session_token")?.value;
  return !!token;
}

function isAdmin(req: NextRequest): boolean {
  const role = req.cookies.get("user_role")?.value;
  return role === "admin";
}

export function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;

  // Request auth for student/admin paths
  if (path.startsWith("/admin") || isStudentPath(path)) {
    if (!hasSession(req)) {
      const loginUrl = new URL("/login", req.url);
      loginUrl.searchParams.set("next", path);
      return NextResponse.redirect(loginUrl);
    }
  }

  // Admin-specific check
  if (path.startsWith("/admin") && !isAdmin(req)) {
    return NextResponse.redirect(new URL("/", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};