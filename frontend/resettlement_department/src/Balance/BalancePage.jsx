import React from "react";
import { DropdownProvider } from "./DropdownContext";
import DropdownButton from "./DropdownButton";
import SubmitButton from "./SubmitButton";
import Aside from "../Navigation/Aside";

export default function BalancePage() {
  const items1 = ['Элемент 1','Элемент 2'];
  const items2 = ['Элемент 3','Элемент 4'];
  const items3 = ['С очередниками','С инвалидами'];

  return (
        <div className="bg-muted/60 flex min-h-screen w-full flex-col">
          <Aside />
          <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100 items-center">
            <DropdownProvider>
              <div className="p-4 justify-items-center bg-white w-1/3 h-[30vh] rounded-xl shadow-xl">
                <div className="flex justify-around w-full">
                  <DropdownButton id="dropdown1" items={items1} />
                  <DropdownButton id="dropdown2" items={items2} />
                </div>
                <div className="m-4 justify-items-center">
                  <DropdownButton id="dropdown3" items={items3} />
                  <SubmitButton />
                </div>
              </div>
            </DropdownProvider>
          </main>
        </div>
  );
}