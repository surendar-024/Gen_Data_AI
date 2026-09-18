import { NextResponse } from "next/server";
import { getCurrentUser } from "@/lib/auth";
import { connectToDatabase } from "@/lib/mongodb";

// GET — list all chats for current user
export async function GET() {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { db } = await connectToDatabase();
    const chats = await db
      .collection("chats")
      .find(
        { userId: user.userId },
        { projection: { title: 1, createdAt: 1, updatedAt: 1 } }
      )
      .sort({ updatedAt: -1 })
      .toArray();

    return NextResponse.json({
      chats: chats.map((c) => ({
        id: c._id.toString(),
        title: c.title,
        createdAt: c.createdAt,
        updatedAt: c.updatedAt,
      })),
    });
  } catch (error) {
    console.error("List chats error:", error);
    return NextResponse.json({ error: "Failed to load chats" }, { status: 500 });
  }
}
