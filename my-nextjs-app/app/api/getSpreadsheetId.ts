// app/api/getSpreadsheetId.ts
import { NextApiRequest, NextApiResponse } from "next";
import { getUserById } from "../../lib/actions/user.actions";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const { userId, type } = req.query;

  if (
    !userId ||
    typeof userId !== "string" ||
    !type ||
    typeof type !== "string"
  ) {
    return res.status(400).json({ error: "Invalid userId or type" });
  }

  try {
    const user = await getUserById(userId);
    let spreadsheetId;

    if (type === "uploadDocumentA") {
      spreadsheetId = user.spreadsheetIds.uploadDocumentA;
    } else if (type === "uploadDocumentBC") {
      spreadsheetId = user.spreadsheetIds.uploadDocumentBC;
    } else {
      return res.status(400).json({ error: "Invalid type" });
    }

    if (!spreadsheetId) {
      return res
        .status(404)
        .json({ error: "Spreadsheet ID not found for the specified type" });
    }

    return res.status(200).json({ spreadsheetId });
  } catch (error) {
    return res.status(500).json({ error: "Failed to fetch spreadsheetId" });
  }
}
