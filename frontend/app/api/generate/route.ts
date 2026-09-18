import { NextRequest, NextResponse } from "next/server";
import { getCurrentUser } from "@/lib/auth";
import { connectToDatabase } from "@/lib/mongodb";
import { ObjectId } from "mongodb";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { prompt, chatId } = await request.json();

    if (!prompt || !prompt.trim()) {
      return NextResponse.json(
        { error: "Prompt is required" },
        { status: 400 }
      );
    }

    // Call the FastAPI backend
    const backendRes = await fetch(`${BACKEND_URL}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: prompt.trim() }),
    });

    if (!backendRes.ok) {
      const errText = await backendRes.text();
      console.error("Backend error:", errText);
      return NextResponse.json(
        { error: "Dataset generation failed. Please try again." },
        { status: 502 }
      );
    }

    const result = await backendRes.json();

    // Save to MongoDB
    const { db } = await connectToDatabase();
    const chatsCollection = db.collection("chats");

    const userMessage = {
      role: "user",
      content: prompt.trim(),
      timestamp: new Date(),
    };

    const assistantMessage = {
      role: "assistant",
      content: `Generated ${result.schema?.rows || result.preview?.length || 0} rows across ${result.schema?.columns?.length || 0} columns`,
      dataset: result.preview || [],
      schema: result.schema || {},
      intent: result.intent || {},
      timestamp: new Date(),
    };

    let finalChatId: string;

    if (chatId) {
      // Append to existing chat
      await chatsCollection.updateOne(
        { _id: new ObjectId(chatId), userId: user.userId },
        {
          $push: {
            messages: { $each: [userMessage, assistantMessage] },
          } as Record<string, unknown>,
          $set: { updatedAt: new Date() },
        }
      );
      finalChatId = chatId;
    } else {
      // Create new chat
      const title =
        prompt.trim().length > 60
          ? prompt.trim().substring(0, 60) + "..."
          : prompt.trim();

      const newChat = await chatsCollection.insertOne({
        userId: user.userId,
        title,
        messages: [userMessage, assistantMessage],
        createdAt: new Date(),
        updatedAt: new Date(),
      });
      finalChatId = newChat.insertedId.toString();
    }

    return NextResponse.json({
      chatId: finalChatId,
      dataset: result.preview || [],
      schema: result.schema || {},
      intent: result.intent || {},
      message: assistantMessage.content,
    });
  } catch (error) {
    console.error("Generate error:", error);
    return NextResponse.json(
      { error: "Something went wrong. Please try again." },
      { status: 500 }
    );
  }
}
