import type React from "react";
import { forwardRef } from "react";
import SvgSberIcon from "./SberIcon";

export const SberIcon = forwardRef<SVGSVGElement, React.PropsWithChildren<{}>>(
  (props, ref) => {
    return <SvgSberIcon ref={ref} {...props} />;
  },
);
