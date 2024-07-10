import { google } from "googleapis";
import { GoogleAuth } from "google-auth-library";

const SCOPES = [
  "https://www.googleapis.com/auth/spreadsheets",
  "https://www.googleapis.com/auth/drive",
];

const base64EncodedServiceAccount =
  process.env.GOOGLE_SHEETS_CREDENTIALS_BASE64 ?? "";
const decodedServiceAccount = Buffer.from(
  base64EncodedServiceAccount,
  "base64"
).toString("utf-8");
const credentials = JSON.parse(decodedServiceAccount);

const auth = new GoogleAuth({
  credentials: credentials,
  scopes: SCOPES,
});

const sheets = google.sheets({ version: "v4", auth });
const drive = google.drive({ version: "v3", auth });

export async function duplicateSpreadsheet(templateId: string, title: string) {
  console.log("Duplicating spreadsheet starting", templateId, title);
  const { data } = await drive.files.copy({
    fileId: templateId,
    requestBody: {
      name: title,
    },
  });

  if (!data.id) {
    throw new Error("Failed to duplicate spreadsheet");
  }
  console.log("Duplicating spreadsheet completed with id:", data.id);
  return data.id;
}

export async function shareSpreadsheet(spreadsheetId: string, email: string) {
  console.log("Sharing spreadsheet starting", spreadsheetId, email);
  await drive.permissions.create({
    fileId: spreadsheetId,
    requestBody: {
      type: "user",
      role: "writer",
      emailAddress: email,
    },
  });
}
