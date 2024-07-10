"use server";

import { revalidatePath } from "next/cache";

import User from "../database/models/user.model";
import { connectToDatabase } from "../database/mongoose";
import { handleError } from "../utils";
import {
  duplicateSpreadsheet,
  shareSpreadsheet,
} from "../../app/api/googleSheets/googleSheetsServices";

// CREATE
export async function createUser(user: CreateUserParams) {
  console.log("Creating user", user);
  try {
    await connectToDatabase();
    const newUser = await User.create(user);
    if (newUser) {
      const templateIdA = process.env.TEMPLATE_SPREADSHEET_ID_A || "";
      const templateIdBC = process.env.TEMPLATE_SPREADSHEET_ID_BC || "";

      const spreadsheetIdA = await duplicateSpreadsheet(
        templateIdA,
        `User_${newUser._id}_DocumentA`
      );
      console.log("spreadsheetIdA created", spreadsheetIdA);
      const spreadsheetIdBC = await duplicateSpreadsheet(
        templateIdBC,
        `User_${newUser._id}_DocumentBC`
      );
      console.log("spreadsheetIdBC created", spreadsheetIdBC);

      await shareSpreadsheet(spreadsheetIdA, newUser.email);
      await shareSpreadsheet(spreadsheetIdBC, newUser.email);

      newUser.spreadsheetIds = {
        uploadDocumentA: spreadsheetIdA,
        uploadDocumentBC: spreadsheetIdBC,
      };
    }

    await newUser.save();
    console.log("spreadsheetIds saved to user", newUser.spreadsheetIds);

    return JSON.parse(JSON.stringify(newUser));
  } catch (error) {
    handleError(error);
  }
}

// READ
export async function getUserById(userId: string) {
  console.log("Fetching user in getUserById", userId);
  try {
    await connectToDatabase();

    const user = await User.findOne({ clerkId: userId });

    if (!user) throw new Error("User not found");

    return JSON.parse(JSON.stringify(user));
  } catch (error) {
    handleError(error);
  }
}

// UPDATE
export async function updateUser(clerkId: string, user: UpdateUserParams) {
  try {
    await connectToDatabase();

    const updatedUser = await User.findOneAndUpdate({ clerkId }, user, {
      new: true,
    });

    if (!updatedUser) throw new Error("User update failed");

    return JSON.parse(JSON.stringify(updatedUser));
  } catch (error) {
    handleError(error);
  }
}

// DELETE
export async function deleteUser(clerkId: string) {
  console.log("Deleting user", clerkId);
  try {
    await connectToDatabase();

    // Find user to delete
    const userToDelete = await User.findOne({ clerkId });

    if (!userToDelete) {
      throw new Error("User not found");
    }

    // Delete user
    const deletedUser = await User.findByIdAndDelete(userToDelete._id);
    revalidatePath("/");

    return deletedUser ? JSON.parse(JSON.stringify(deletedUser)) : null;
  } catch (error) {
    handleError(error);
  }
}

// USE CREDITS
export async function updateCredits(userId: string, creditFee: number) {
  try {
    await connectToDatabase();

    const updatedUserCredits = await User.findOneAndUpdate(
      { _id: userId },
      { $inc: { creditBalance: creditFee } },
      { new: true }
    );

    if (!updatedUserCredits) throw new Error("User credits update failed");

    return JSON.parse(JSON.stringify(updatedUserCredits));
  } catch (error) {
    handleError(error);
  }
}
