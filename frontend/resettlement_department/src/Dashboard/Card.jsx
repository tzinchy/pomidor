import React from "react";
import { SVGs } from "./DashboardSvg";

export default function Card({value}){

  return (
      <a href={value.link} className="w-1/6 bg-white text-card-foreground rounded-lg border shadow-sm hover:from-muted hover:to-background/25 cursor-pointer hover:bg-gradient-to-tl col-span-3 sm:col-span-2 lg:col-span-1">
        <div >
          <div className="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
            <h3 className="tracking-tight line-clamp-2 text-sm font-bold">{value.name}</h3>
            <SVGs state={value.svg} />
          </div>
          <div className="p-6 pt-0">
            <div className={"text-4xl font-bold " + value.color}>{value.value}</div>
            <p className="text-muted-foreground text-xs">площадок(и)</p>
          </div>
        </div>
      </a>
  )
}