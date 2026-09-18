import { NextRequest, NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";
import bcrypt from "bcryptjs";
import { createToken, setAuthCookie } from "@/lib/auth";

export async function POST(request: NextRequest) {
  try {
    const { identifier, password } = await request.json();

    // Validate input
    if (!identifier || !password) {
      return NextResponse.json(
        { error: "Please enter your email/username and password" },
        { status: 400 }
      );
    }

    const { db } = await connectToDatabase();
    const usersCollection = db.collection("users");

    // Find user by email or username
    const user = await usersCollection.findOne({
      $or: [
        { email: identifier.toLowerCase() },
        { username: identifier.toLowerCase() },
      ],
    });

    if (!user) {
      return NextResponse.json(
        { error: "No account found with these credentials" },
        { status: 401 }
      );
    }

    // Verify password
    const isPasswordValid = await bcrypt.compare(password, user.password);

    if (!isPasswordValid) {
      return NextResponse.json(
        { error: "Incorrect password. Please try again." },
        { status: 401 }
      );
    }

    // Create JWT and set cookie
    const token = await createToken({
      userId: user._id.toString(),
      username: user.username,
      email: user.email,
    });

    await setAuthCookie(token);

    return NextResponse.json({
      message: "Logged in successfully",
      user: {
        id: user._id.toString(),
        username: user.username,
        displayName: user.displayName || user.username,
        email: user.email,
      },
    });
  } catch (error) {
    console.error("Login error:", error);
    return NextResponse.json(
      { error: "Something went wrong. Please try again." },
      { status: 500 }
    );
  }
}
