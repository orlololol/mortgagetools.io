import Header from "@/components/shared/Header";
import PDFUploadForm from "@/components/shared/PDFUploader";
import { transformationTypes } from "@/constants";
import { getUserById } from "@/lib/actions/user.actions";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { useEffect } from "react";

// Define the type for transformation types
type TransformationTypeKey = keyof typeof transformationTypes;

interface SearchParamProps {
  params: { type: TransformationTypeKey };
}

const AddTransformationTypePage = async ({
  params: { type },
}: SearchParamProps) => {
  const { userId } = auth();

  if (!userId) {
    redirect("/sign-in");
  }

  const user = await getUserById(userId);

  if (!user) {
    redirect("/sign-in");
  }

  const transformation = transformationTypes[type];

  if (!transformation) {
    redirect("/404"); // Handle invalid transformation type
  }

  // let excel_link;

  // const handleExcelLink = () => {
  //   if (type === "uploadDocumentA") {
  //     excel_link =
  //       "https://docs.google.com/spreadsheets/d/1P2nfwGknVV6U1BX0CsYtz0ETgppKCb1-3OAys5zeUt8/edit?usp=sharing";
  //     return excel_link;
  //   } else if (type === "uploadDocumentBC") {
  //     excel_link =
  //       "https://docs.google.com/spreadsheets/d/1NJD5DWHMscbTjvMeQwSRehu27p8If8SN_BY1G42Il1w/edit?usp=sharing";
  //     return excel_link;
  //   }
  // };

  return (
    <>
      <section className="mt-10">
        <Header
          title={transformation.title}
          subtitle={transformation.subTitle}
        />
        <div className="mt-8">
          <PDFUploadForm
            action="Add"
            clerkId={user.clerkId}
            type={transformation.type as TransformationTypeKey}
            creditBalance={user.creditBalance}
            // documentUrl={handleExcelLink()}
          />
        </div>
      </section>
    </>
  );
};

export default AddTransformationTypePage;
