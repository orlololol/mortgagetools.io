"use client";

import { useEffect, useState, useTransition } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  updateCredits,
  getUserIdFromClerkId,
} from "@/lib/actions/user.actions";
import { creditFee } from "@/constants";
import { CustomField } from "./CustomField";
import { ConfirmationModal } from "./ConfirmationModal";
import { InsufficientCreditsModal } from "./InsufficientCreditsModal";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

const fileSchema = z.object({
  file: z.union([z.instanceof(File), z.undefined()]).refine(
    (file) => {
      if (file === undefined) {
        return true;
      }
      return file.type === "application/pdf";
    },
    {
      message: "File must be a PDF",
    }
  ),
});

export const formSchema = z.object({
  document_type: z.string().min(1, "Title is required"),
  files: z.array(fileSchema).min(1, "At least one file is required"),
});

type FormValues = z.infer<typeof formSchema>;

interface PDFUploadFormProps {
  action: "Add" | "Update";
  clerkId: string;
  type: "uploadDocumentA" | "uploadDocumentBC";
  creditBalance: number;
  data?: Partial<FormValues> & { _id?: string };
  documentUrl?: string;
}

const PDFUploadForm: React.FC<PDFUploadFormProps> = ({
  action,
  clerkId,
  type,
  creditBalance,
  data = null,
  documentUrl,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPending, startTransition] = useTransition();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [spreadsheetId, setSpreadsheetId] = useState<string | null>(null);
  const router = useRouter();

  const initialValues =
    data?.document_type && action === "Update"
      ? {
          document_type: data.document_type,
          files: data.files || [{ file: undefined }],
        }
      : ({
          document_type: "1040",
          files: [{ file: undefined }],
        } as unknown as FormValues);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: initialValues,
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "files",
  });

  useEffect(() => {
    const fetchSpreadsheetId = async () => {
      try {
        console.log("Fetching spreadsheet ID for user:", clerkId);
        const response = await fetch(
          `/api/getSpreadsheetId?userId=${clerkId}&type=${type}`
        );
        if (!response.ok) {
          console.error("Failed to fetch spreadsheet ID", response.status);
          throw new Error("Failed to fetch spreadsheet ID");
        }
        const data = await response.json();
        setSpreadsheetId(data.spreadsheetId);
      } catch (error) {
        console.error("Error fetching spreadsheet ID:", error);
      }
    };

    fetchSpreadsheetId();
  }, [clerkId, type]);

  const onProcessHandler = () => {
    if (creditBalance < Math.abs(creditFee)) {
      alert("You do not have enough credits to process the PDF.");
      return;
    }
    setIsModalOpen(true);
  };

  const handleConfirmProcess = () => {
    setIsModalOpen(false);
    setIsProcessing(true);
    form.handleSubmit(onSubmit)();
  };

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      const formData = new FormData();
      formData.append(
        "document_type",
        type === "uploadDocumentBC" ? values.document_type : "1040"
      );
      formData.append("spreadsheetId", spreadsheetId || "");

      if (values.files[0]?.file) {
        formData.append("file", values.files[0].file);
      } else {
        throw new Error("No file selected");
      }

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "";
      const response = await fetch(backendUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Failed to process PDF: ${await response.text()}`);
      }

      const result = await response.json();
      console.log("Processing result:", result);
      const userId = await getUserIdFromClerkId(clerkId);
      // Deduct credits after successful processing
      await updateCredits(userId, creditFee);

      // Optionally, show a success message or redirect the user
      alert("PDF processed successfully and credits deducted.");
      // router.push('/success-page');
    } catch (error) {
      console.error("Error processing PDF:", error);
      alert("An error occurred while processing the PDF. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  }

  return (
    <div>
      <Form {...form}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onProcessHandler();
          }}
          className="space-y-8"
        >
          {creditBalance < Math.abs(creditFee) && <InsufficientCreditsModal />}
          <div className="flex flex-row space-x-20">
            <div className="my-4">
              {type === "uploadDocumentBC" && (
                <FormField
                  control={form.control}
                  name="document_type"
                  render={({ field }) => (
                    <FormItem className="space-y-3">
                      <FormLabel>Choose your file type</FormLabel>
                      <RadioGroup
                        onValueChange={field.onChange}
                        className="flex flex-col space-y-1"
                      >
                        <FormItem className="flex items-center space-x-3 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="w2" />
                          </FormControl>
                          <FormLabel className="font-normal">W-2</FormLabel>
                        </FormItem>
                        <FormItem className="flex items-center space-x-3 space-y-0">
                          <FormControl>
                            <RadioGroupItem value="paystub" />
                          </FormControl>
                          <FormLabel className="font-normal">Paystub</FormLabel>
                        </FormItem>
                      </RadioGroup>
                    </FormItem>
                  )}
                />
              )}

              <div className="space-y-5">
                <div className="mt-8">
                  {fields.map((field, index) => (
                    <FormItem key={field.id}>
                      <FormLabel>Upload PDF</FormLabel>
                      <FormControl>
                        <Input
                          type="file"
                          accept=".pdf"
                          onChange={(
                            e: React.ChangeEvent<HTMLInputElement>
                          ) => {
                            const file = e.target.files?.[0];
                            if (file) {
                              form.setValue(`files.${index}.file`, file);
                            }
                          }}
                          className="input-field"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  ))}
                </div>
                <div className="flex flex-col gap-4">
                  <Button
                    type="button"
                    className="submit-button capitalize"
                    disabled={
                      isProcessing || creditBalance < Math.abs(creditFee)
                    }
                    onClick={onProcessHandler}
                  >
                    {isProcessing ? "Processing..." : "Process PDFs"}
                  </Button>
                </div>
              </div>
            </div>
            <div>
              {spreadsheetId && (
                <iframe
                  src={`https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit?usp=sharing`}
                  width="700px"
                  height="700px"
                ></iframe>
              )}
            </div>
          </div>
        </form>
        <ConfirmationModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onConfirm={handleConfirmProcess}
        />
      </Form>
    </div>
  );
};

export default PDFUploadForm;
