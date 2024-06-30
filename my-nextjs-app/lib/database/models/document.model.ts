import { Document, Schema, model, models } from "mongoose";

export interface IDocumentProcess extends Document {
  title: string;
  documentType: string;
  status: string;
  userId: string;
  createdAt?: Date;
  updatedAt?: Date;
}

const DocumentProcessSchema = new Schema({
  title: { type: String, required: true },
  documentType: { type: String, required: true },
  status: { type: String, required: true },
  userId: { type: Schema.Types.ObjectId, ref: "User" },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now },
});

const DocumentProcess =
  models?.DocumentProcess || model("DocumentProcess", DocumentProcessSchema);

export default DocumentProcess;
