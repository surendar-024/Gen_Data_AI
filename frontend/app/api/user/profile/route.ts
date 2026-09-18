import { NextRequest, NextResponse } from "next/server";
import { getCurrentUser, createToken, setAuthCookie } from "@/lib/auth";
import { connectToDatabase } from "@/lib/mongodb";
import { ObjectId } from "mongodb";
import bcrypt from "bcryptjs";

// PUT — update profile (username)
export async function PUT(request: NextRequest) {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { username } = await request.json();

    if (!username || username.trim().length < 3) {
      return NextResponse.json(
        { error: "Username must be at least 3 characters" },
        { status: 400 }
      );
    }

    const { db } = await connectToDatabase();
    const usersCollection = db.collection("users");

    // Check if username is taken
    const existing = await usersCollection.findOne({
      username: username.toLowerCase(),
      _id: { $ne: new ObjectId(user.userId) },
    });

    if (existing) {
      return NextResponse.json(
        { error: "This username is already taken" },
        { status: 409 }
      );
    }

    await usersCollection.updateOne(
      { _id: new ObjectId(user.userId) },
      {
        $set: {
          username: username.toLowerCase(),
          displayName: username,
          updatedAt: new Date(),
        },
      }
    );

    // Refresh JWT with new username
    const newToken = await createToken({
      userId: user.userId,
      username: username.toLowerCase(),
      email: user.email,
    });
    await setAuthCookie(newToken);

    return NextResponse.json({
      message: "Profile updated",
      user: { username: username.toLowerCase(), displayName: username },
    });
  } catch (error) {
    console.error("Profile update error:", error);
    return NextResponse.json(
      { error: "Failed to update profile" },
      { status: 500 }
    );
  }
}

// DELETE — delete account
export async function DELETE() {
  try {
    const user = await getCurrentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { db } = await connectToDatabase();

    // Delete all user's chats
    await db.collection("chats").deleteMany({ userId: user.userId });

    // Delete user account
    await db
      .collection("users")
      .deleteOne({ _id: new ObjectId(user.userId) });

    return NextResponse.json({ message: "Account deleted" });
  } catch (error) {
    console.error("Delete account error:", error);
    return NextResponse.json(
      { error: "Failed to delete account" },
      { status: 500 }
    );
  }
}
