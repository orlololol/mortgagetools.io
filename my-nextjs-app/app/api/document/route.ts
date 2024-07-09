import { getUserById } from "@/lib/actions/user.actions";
import { auth } from "@clerk/nextjs/server";

const API_BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL; // hard coded for now, change at prod

export async function POST(req: any, res: any) {
  try {
    const user = await getUserById(req.body.userId);
    if (!user) {
      return res.status(404).json({ message: "User not found" });
    }

    const response = await fetch(`${API_BACKEND_URL}/process`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        userId: req.body.userId,
        document: req.body.document,
      }),
    });

    return res.status(response.status).json(await response.json());
  } catch (error: any) {
    return res.status(500).json({ message: error.message });
  }
}
