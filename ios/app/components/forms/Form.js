import React from "react";
import { Formik } from "formik";

function AppForm({
  initialValues,
  onSubmit,
  validationSchema,
  children,
  innerRef,
  enableReinitialize = false,
}) {
  return (
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
      innerRef={innerRef}
      enableReinitialize={enableReinitialize}
    >
      {() => <>{children}</>}
    </Formik>
  );
}

export default AppForm;
