import { NextRequest, NextResponse } from "next/server";
import { getUserById } from "../../../lib/actions/user.actions";

const MAX_ATTEMPTS = 30;
const DELAY_MS = 1000;

async function waitForSpreadsheetCreation(userId: string): Promise<any> {
  let attempts = 0;
  while (attempts < MAX_ATTEMPTS) {
    const user = await getUserById(userId);
    if (user.spreadsheetStatus === "completed") {
      return user;
    } else if (user.spreadsheetStatus === "error") {
      throw new Error("Spreadsheet creation failed");
    }
    await new Promise((resolve) => setTimeout(resolve, DELAY_MS));
    attempts++;
  }
  throw new Error("Spreadsheet creation timed out");
}

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
    let user = await getUserById(userId);
    console.log("Fetched user data:", user);

    if (user.spreadsheetStatus === "pending") {
      console.log("Spreadsheet creation in progress. Waiting...");
      user = await waitForSpreadsheetCreation(userId);
    }

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
