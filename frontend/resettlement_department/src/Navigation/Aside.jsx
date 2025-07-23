import React from "react";
import LinkButton from "./LinkButton/LinkButton";
import UpdateDataButton from "./UpdateInfo/UpdateModal";
import { canSeeDashboard } from "..";

export default function Aside() {



  return (
    <aside className="bg-neutral-100 fixed inset-y-0 left-0 z-[105] hidden w-14 flex-col justify-between border-r p-2 sm:flex">
      <nav className="items-centergap-4 flex flex-col gap-2">
        {canSeeDashboard && <LinkButton name="dashboard" />}
        {canSeeDashboard && <LinkButton name="table_page" />}
        <LinkButton name="aparts" />
        {canSeeDashboard && <LinkButton name="balance" />}
        <LinkButton name="cin" />
        
        {canSeeDashboard && <UpdateDataButton />}
      </nav>
    </aside>
  );
}

