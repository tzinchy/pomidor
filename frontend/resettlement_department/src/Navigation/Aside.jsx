import React from "react";
import LinkButton from "./LinkButton/LinkButton";
import UpdateDataButton from "./UpdateInfo/UpdateModal";
import { canSeeDashboard } from "..";
import { LogOut } from "lucide-react";
import LogoutButton from "./LogoutButton";
import { ASIDECOLOR } from "..";

export default function Aside() {

  console.log('ASIDECOLOR', ASIDECOLOR);

  return (
    <aside className={`fixed bg-${ASIDECOLOR} inset-y-0 left-0 z-[105] hidden w-14 flex-col justify-between border-r p-2 sm:flex`}>
      <nav className="items-centergap-4 flex flex-col gap-2">
        {canSeeDashboard && <LinkButton name="dashboard" />}
        {canSeeDashboard && <LinkButton name="table_page" />}
        <LinkButton name="aparts" />
        {canSeeDashboard && <LinkButton name="balance" />}
        <LinkButton name="cin" />
      </nav>
      <div className="mt-auto flex flex-col items-center gap-2 pt-2">
        {canSeeDashboard && <UpdateDataButton />}
        <LogoutButton />
      </div>
    </aside>
  );
}

