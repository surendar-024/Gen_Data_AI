import { NextRequest, NextResponse } from "next/server";
import { getCurrentUser } from "@/lib/auth";
import { connectToDatabase } from "@/lib/mongodb";
import { ObjectId } from "mongodb";

// GET — load a single chat with messages
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;

    if (!ObjectId.isValid(id)) {
      return NextResponse.json({ error: "Invalid chat ID" }, { status: 400 });
    }

    const { db } = await connectToDatabase();
    const chat = await db
      .collection("chats")
      .findOne({ _id: new ObjectId(id), userId: user.userId });

    if (!chat) {
      return NextResponse.json({ error: "Chat not found" }, { status: 404 });
    }

    return NextResponse.json({
      id: chat._id.toString(),
      title: chat.title,
      messages: chat.messages,
      createdAt: chat.createdAt,
      updatedAt: chat.updatedAt,
    });
  } catch (error) {
    console.error("Get chat error:", error);
    return NextResponse.json(
      { error: "Failed to load chat" },
      { status: 500 }
    );
  }
}

// PUT — rename chat
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;
    const { title } = await request.json();

    if (!title || !title.trim()) {
      return NextResponse.json(
        { error: "Title is required" },
        { status: 400 }
      );
    }

    const { db } = await connectToDatabase();
    const result = await db.collection("chats").updateOne(
      { _id: new ObjectId(id), userId: user.userId },
      { $set: { title: title.trim(), updatedAt: new Date() } }
    );

    if (result.matchedCount === 0) {
      return NextResponse.json({ error: "Chat not found" }, { status: 404 });
    }

    return NextResponse.json({ message: "Chat renamed" });
  } catch (error) {
    console.error("Rename chat error:", error);
    return NextResponse.json(
      { error: "Failed to rename chat" },
      { status: 500 }
    );
  }
}

// DELETE — delete a chat
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { id } = await params;

    const { db } = await connectToDatabase();
    const result = await db
      .collection("chats")
      .deleteOne({ _id: new ObjectId(id), userId: user.userId });

    if (result.deletedCount === 0) {
      return NextResponse.json({ error: "Chat not found" }, { status: 404 });
    }

    return NextResponse.json({ message: "Chat deleted" });
  } catch (error) {
    console.error("Delete chat error:", error);
    return NextResponse.json(
      { error: "Failed to delete chat" },
      { status: 500 }
    );
  }
}
