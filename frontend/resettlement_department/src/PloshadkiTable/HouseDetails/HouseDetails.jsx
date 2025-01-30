import React from "react";

export default function HouseDetails({ addressHouseDetails, houseDetails, setIsDetailsVisible, setOpendDetailsId }) {
  function handleClose() {
    setIsDetailsVisible(null);
    setOpendDetailsId(null);
  }

  const val = houseDetails['0']

  if (val !== undefined){console.log('DANNIE', val[1])}

  return (
    <div
      className={`relative z-20 flex flex-col bg-white rounded transition-all duration-300 shadow-lg
      w-full sm:w-2/4 md:w-1/3 lg:max-w-[25%]`}
      style={{minWidth:500+'px'}}
    >
      <div className="space-y-1.5 p-6 flex flex-row items-center gap-2 transition-all ease-in-out h-16 py-3">
        <div className="flex flex-col">
          <h3 className="text-2xl font-semibold leading-none tracking-tight">{addressHouseDetails.f1}</h3>
          <p className="text-muted-foreground text-sm"></p>
        </div>
      </div>
      
      <div className="p-6 flex h-[95%] flex-col gap-3 pt-2">
        <div dir="ltr" className="relative overflow-auto rounded border w-full flex-1 scrollbar-custom">
          <div data-radix-scroll-area-viewport="" className="relative w-full rounded-[inherit]">
            <div>
              {val && val[1] ? val[1].map((item, index) => (
                <div key={index} className="relative w-full hover:bg-gray-50">
                  <div className="border-b group relative">
                    <h3 className="flex">
                      <button
                        type="button"
                        aria-controls={`radix-:r${index}`} // Сделаем ID динамическим для каждого элемента
                        aria-expanded="false"
                        className="flex flex-1 items-center justify-between font-medium transition-all hover:underline [&[data-state=open]>svg]:rotate-180 data-[state=open]:bg-muted group-hover:bg-muted/50 py-2 pl-2 pr-4 text-left text-xs group-hover:no-underline"
                      >
                        <div className="flex flex-row justify-start items-center gap-2 w-full truncate flex-wrap">
                          <div className="relative p-2" data-state="closed">
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              width="24"
                              height="24"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              strokeWidth="2"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              className="lucide lucide-circle-x h-8 w-8 text-red-500"
                            >
                              <circle cx="12" cy="12" r="10"></circle>
                              <path d="m15 9-6 6"></path>
                              <path d="m9 9 6 6"></path>
                            </svg>
                          </div>
                          <div className="flex flex-col justify-start items-start gap-0 flex-1 truncate">
                            <div className="flex-1 truncate">
                              <span className="font-bold">кв.{item.apartNum}</span>
                              <span className="px-1">{item.fio}</span>
                              {item.problems.includes("Суды") ? (<div className="inline-flex items-center rounded-full border py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground ml-1 h-4 px-1 text-xs bg-rose-100 border-rose-200">Суды</div>) : ''}
                              {item.problems.includes("Отказ") ? (<div className="inline-flex items-center rounded-full border py-0.5 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 text-foreground ml-1 h-4 px-1 text-xs bg-amber-100 border-amber-200">Отказ</div>) : ''}
                            </div>
                            <div className="text-muted-foreground flex-1 truncate">{item.action}</div>
                          </div>
                        </div>
                      </button>
                    </h3>
                  </div>
                </div>
              )) : (
                <div className="relative flex flex-col place-items-center py-4 text-gray-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-cat stroke-muted-foreground h-12 w-12 stroke-1">
                    <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2 5.03-2.84 6.42-2.26 1.4.58-.42 7-.42 7 .57 1.07 1 2.24 1 3.44C21 17.9 16.97 21 12 21s-9-3-9-7.56c0-1.25.5-2.4 1-3.44 0 0-1.89-6.42-.5-7 1.39-.58 4.72.23 6.5 2.23A9.04 9.04 0 0 1 12 5Z"></path>
                    <path d="M8 14v.5"></path>
                    <path d="M16 14v.5"></path>
                    <path d="M11.25 16.25h1.5L12 17l-.75-.75Z"></path>
                  </svg>
                  <div>Нет данных для отображения</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

          <button className="inline-flex items-center justify-center whitespace-nowrap text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 underline-offset-4 hover:underline h-10 group absolute right-2 top-2 rounded-full p-2"
            onClick={handleClose}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-x stroke-muted-foreground opacity-50 group-hover:opacity-100">
            <path d="M18 6 6 18"></path>
            <path d="m6 6 12 12"></path>
            </svg>
          </button>
      </div>
  );
}
