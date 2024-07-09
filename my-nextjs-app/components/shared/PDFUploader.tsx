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
import { CustomField } from "./CustomField";
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
  userId: string;
  type: "uploadDocumentA" | "uploadDocumentBC";
  creditBalance: number;
  data?: Partial<FormValues> & { _id?: string };
  documentUrl?: string;
}

const PDFUploadForm: React.FC<PDFUploadFormProps> = ({
  action,
  userId,
  type,
  creditBalance,
  data = null,
  documentUrl,
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPending, startTransition] = useTransition();
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
        const response = await fetch(
          `/api/getSpreadsheetId?userId=${userId}&type=${type}`
        );
        if (!response.ok) {
          throw new Error("Failed to fetch spreadsheet ID");
        }
        const data = await response.json();
        setSpreadsheetId(data.spreadsheetId);
      } catch (error) {
        console.error("Error fetching spreadsheet ID:", error);
      }
    };

    fetchSpreadsheetId();
  }, [userId, type]);

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setIsSubmitting(true);

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
        console.error("No file selected");
        setIsSubmitting(false);
        return;
      }

      console.log("FormData contents:");
      for (let [key, value] of formData.entries()) {
        console.log(key, value);
      }

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "";
      const response = await fetch(backendUrl, {
        method: "POST",
        body: formData,
      });

      console.log("Response status:", response.status);

      const responseText = await response.text();
      console.log("Response text:", responseText);

      if (!response.ok) {
        throw new Error(`Failed to process PDF: ${responseText}`);
      }

      const result = JSON.parse(responseText);
      console.log("Processing result:", result);
    } catch (error) {
      console.error("Error processing PDF:", error);
    }

    setIsSubmitting(false);
  }

  const onProcessHandler = async () => {
    setIsProcessing(true);

    // Pre-processing logic here
    // Example: Check if the user has enough credits
    if (creditBalance <= 0) {
      alert("You do not have enough credits to process the PDF.");
      setIsProcessing(false);
      return;
    }

    // Example: Confirm user action
    const userConfirmed = confirm("Are you sure you want to process the PDFs?");
    if (!userConfirmed) {
      setIsProcessing(false);
      return;
    }

    // // Example: Deduct credits from user's balance
    // try {
    //   await deductCredits(userId, creditFee);
    // } catch (error) {
    //   console.error("Failed to deduct credits:", error);
    //   alert("Failed to deduct credits. Please try again.");
    //   setIsProcessing(false);
    //   return;
    // }

    // Proceed with the main processing logic
    startTransition(async () => {
      // Your processing logic here
    });

    setIsProcessing(false);
  };

  return (
    <div>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
          {creditBalance < 0 && <InsufficientCreditsModal />}
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
                    disabled={isProcessing}
                    onClick={() => onSubmit(form.getValues())}
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
      </Form>
    </div>
  );
};

export default PDFUploadForm;
