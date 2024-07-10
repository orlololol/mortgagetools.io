import { google } from "googleapis";
import { JWT } from "google-auth-library";

const CLIENT_EMAIL = process.env.GOOGLE_SHEETS_CLIENT_EMAIL;
const PRIVATE_KEY = process.env.GOOGLE_SHEETS_PRIVATE_KEY?.replace(
  /\\n/g,
  "\n"
);
const SCOPES = [
  "https://www.googleapis.com/auth/spreadsheets",
  "https://www.googleapis.com/auth/drive",
];

const auth = new JWT({
  email: CLIENT_EMAIL,
  key: PRIVATE_KEY,
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
