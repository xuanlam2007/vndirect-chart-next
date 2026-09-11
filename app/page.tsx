"use client";

import { useState } from "react";
import Chart from "@/components/Chart";
import KLineChart from "@/components/KLineChart";

export default function Page() {
  const [engine, setEngine] = useState<"lightweight" | "kline">("lightweight");
  return engine === "lightweight"
    ? <Chart onSelectKLine={() => setEngine("kline")} />
    : <KLineChart onSelectLightweight={() => setEngine("lightweight")} />;
}
