import React, { useState } from "react";
import {StatusIcon, RiskIcon} from './Icons';

export function TableHead({ headers }) {
    return (
      <thead className="border-b sticky top-0 z-10 backdrop-blur-md shadow">
        <tr className="hover:bg-muted/50 transition-colors">
          {headers.map((header, index) => (
            <th
              key={index}
              className="px-4 font-medium h-12 text-slate-500 items-center text-start align-middle text-slate-400"
            >
              {header}
            </th>
          ))}
        </tr>
      </thead>
    );
  }
  
export function TableBody({ data }) {
    return (
      <tbody className="text-xs">
        {data.map((item, index) => (
          <React.Fragment key={index}>
            <MainRow index={item} />
            {Object.keys(item[4])
              .slice(1)
              .map((key, subIndex) => (
                <DopRow key={subIndex} details={item[4][key]} />
              ))}
          </React.Fragment>
        ))}
      </tbody>
    );
  }
  
function MainRow({ index }) {
    const details = index[4][Object.keys(index[4])[0]];
  
    return (
      <tr className="bg-white border-b transition-colors">
          <td className="p-2" rowSpan={Object.keys(index[4]).length}>
              <div>
              <div className="text-sm">{index[1]}</div>
              <div className="text-slate-400">{index[2]}</div>
              </div>
          </td>
          <td className="p-2" rowSpan={Object.keys(index[4]).length}>
              {index[3]}
          </td>
          <td className="p-2" rowSpan={Object.keys(index[4]).length}>
              <div className="flex flex-row justify-start items-center gap-2 w-max flex-wrap p-4 w-full">
                  <StatusIcon status={index[7]} />
                  <div className="flex flex-col justify-center items-start gap-0 flex-wrap">
                      <div className="truncate whitespace-nowrap text-sm">{index[6]}</div>
                      <div className="text-slate-500 truncate whitespace-nowrap text-xs">
                          {index[7]}
                      </div>
                  </div>
              </div>
          </td>
          <td className="p-2" rowSpan={Object.keys(index[4]).length}>
              <div className="flex flex-row justify-start items-center gap-2 min-w-[204px] flex-wrap p-4 w-full">
                  <RiskIcon risk={index[5]} />
                  <div className="flex flex-col justify-center items-start gap-0 w-[140px] text-left flex-wrap text-sm">
                      <div className="w-full truncate">{index[5]}</div>
                  </div>
              </div>
          </td>
          <RenderRowDetails details={details} />
      </tr>
    );
  }
  
function DopRow({ details }) {
    return (
      <tr className="bg-white border-b transition-colors">
        <RenderRowDetails details={details} />
      </tr>
    );
  }


  function RenderRowDetails({ details }) {
    const progressColors = {
      mfr: "#a78bfa",
      done: "#10b981",
      risk: "#fb7185",
      attention: "#fbbf24",
      none: "#38bdf8",
    };
  
    const [isHovered, setIsHovered] = useState(false);
  
    const renderProgress = () => {
      const total = details.f6.total;
      const segments = ["mfr", "done", "risk", "attention", "none"].map((key) => ({
        key,
        value: details.f6.deviation[key],
        percentage: (details.f6.deviation[key] / total) * 100,
        color: progressColors[key],
        description: getSegmentDescription(key), // Опциональное описание
      }));
  
      function getSegmentDescription(key) {
        const descriptions = {
          mfr: "в работе у МФР",
          done: "работа завершена",
          risk: "наступили риски",
          attention: "требует внимания",
          none: "без отклонений",
        };
        return descriptions[key] || "";
      }
  
      return (
        <div
          className="relative w-full flex items-center"
        >
          {/* График */}
          <div className="relative h-6 w-full bg-slate-200 rounded-md overflow-hidden flex" onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)}>
            {segments.map(({ key, percentage, color, value }) =>
              percentage > 0 ? (
                <div
                  key={key}
                  className="h-6 relative"
                  style={{
                    width: `${percentage}%`,
                    backgroundColor: color,
                  }}
                >
                  {/* Отображение значения внутри сегмента */}
                  {percentage >= 10 && (
                    <div className="absolute inset-0 flex items-center font-bold justify-center text-xs text-white">
                      {value}
                    </div>
                  )}
                </div>
              ) : null
            )}
          </div>
      
            <div className={`absolute left-[-220px] top-[-10] w-[200px] z-10  bg-white border border-slate-200 rounded-lg shadow-lg transition-all duration-200 ${isHovered ? 'opacity-1 pointer-events-none' : 'opacity-0'}`}>
              <table className="caption-bottom w-full text-sm">
                <thead className="[&_tr]:border-b">
                  <tr className="border-b transition-colors bg-slate-50 text-center text-xs hover:bg-slate-50">
                    <th
                      className="text-slate-500 align-middle font-medium [&:has([role=checkbox])]:pr-0 h-8 min-w-[60px] truncate px-2 text-left"
                      colSpan="3"
                    >
                      {details.f1}
                    </th>
                  </tr>
                </thead>
                <tbody className="[&_tr:last-child]:border-0">
                  {segments.map(
                    ({ key, value, percentage, color, description }) =>
                      percentage > 0 && (
                        <tr
                          key={key}
                          className="hover:bg-muted/50 border-b transition-colors text-slate-500"
                        >
                          <td className="align-middle [&:has([role=checkbox])]:pr-0 px-2 py-1 text-center text-xs">
                            <div
                              className="flex h-4 w-4 rounded"
                              style={{ backgroundColor: color }}
                            ></div>
                          </td>
                          <td className="align-middle [&:has([role=checkbox])]:pr-0 px-0 py-1 text-right text-xs font-bold">
                            {value}
                          </td>
                          <td className="align-middle [&:has([role=checkbox])]:pr-0 px-4 py-1 text-left text-xs">
                            {description}
                          </td>
                        </tr>
                      )
                  )}
                </tbody>
              </table>

              <span className="absolute -rotate-90 top-1/2 -right-2">
                <svg width="10" height="5" viewBox="0 0 30 10" preserveAspectRatio="none" className="block">
                  <polygon points="0,0 30,0 15,10"></polygon>
                </svg>
              </span>
            </div>
        </div>
      );
      
    };
  
    return (
      <>
        <td className="border-l border-b">
          <div className="p-4 w-full">{details.f1}</div>
        </td>
        <td className="border-b">
          <div className="flex flex-row justify-start items-center gap-2 w-max flex-wrap p-4 w-full">
            <StatusIcon status={details.f3} />
            <div className="flex flex-col justify-center items-start gap-0 flex-wrap">
              <div className="truncate whitespace-nowrap">{details.f7}</div>
              <div className="text-slate-500 truncate whitespace-nowrap text-xs">
                {details.f3}
              </div>
            </div>
          </div>
        </td>
        <td className="border-b">
          <div className="flex flex-row justify-start items-center gap-2 min-w-[204px] flex-wrap p-4 w-full">
            <RiskIcon risk={details.f2} />
            <div className="flex flex-col justify-center items-start gap-0 w-[140px] text-left flex-wrap">
              <div className="w-full truncate">{details.f4}</div>
              <div className="text-slate-500 w-full truncate ">{details.f2}</div>
            </div>
          </div>
        </td>
        <td className="border-b">
          <div className="flex flex-col justify-center items-start gap-0 w-[140px] text-left flex-wrap p-4 w-full">
            <div className="text-slate-500 w-full truncate">
              {details.f5.plan.firstResetlementStart}
            </div>
            <div className="w-full truncate ">
              {details.f5.actual.firstResetlementStart || ""}
            </div>
          </div>
        </td>
        <td className="border-b">
          <div className="p-4 min-w-[204px]">{renderProgress()}</div>
        </td>
      </>
    );
  }
  