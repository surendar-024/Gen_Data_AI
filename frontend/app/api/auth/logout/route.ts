import { NextResponse } from "next/server";
import { removeAuthCookie } from "@/lib/auth";

export async function POST() {
  try {
    await removeAuthCookie();
    return NextResponse.json({ message: "Logged out successfully" });
  } catch {
    return NextResponse.json(
      { error: "Failed to logout" },
      { status: 500 }
    );
  }
}
