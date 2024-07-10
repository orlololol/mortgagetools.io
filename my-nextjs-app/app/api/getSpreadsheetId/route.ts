import { NextRequest, NextResponse } from "next/server";
import { getUserById } from "../../../lib/actions/user.actions";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const userId = searchParams.get("userId");
  const type = searchParams.get("type");

  console.log("Received request with userId:", userId, "and type:", type);

  if (!userId || !type) {
    return NextResponse.json(
      { error: "Invalid userId or type" },
      { status: 400 }
    );
  }

  try {
    const user = await getUserById(userId);
    console.log("Fetched user data:", user);

    let spreadsheetId;

    if (type === "uploadDocumentA") {
      spreadsheetId = user.spreadsheetIds.uploadDocumentA;
    } else if (type === "uploadDocumentBC") {
      spreadsheetId = user.spreadsheetIds.uploadDocumentBC;
    } else {
      return NextResponse.json({ error: "Invalid type" }, { status: 400 });
    }

    if (!spreadsheetId) {
      return NextResponse.json(
        { error: "Spreadsheet ID not found for the specified type" },
        { status: 404 }
      );
    }

    return NextResponse.json({ spreadsheetId });
  } catch (error) {
    console.error("Error fetching spreadsheetId:", error);
    return NextResponse.json(
      { error: "Failed to fetch spreadsheetId" },
      { status: 500 }
    );
  }
}
