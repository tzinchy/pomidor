import React from "react";
import LinkButton from "./LinkButton/LinkButton";

export default function Aside() {
  return (
    <aside className="bg-neutral-100 fixed inset-y-0 left-0 z-10 hidden w-14 flex-col justify-between border-r p-2 sm:flex">
      <nav className="items-centergap-4 flex flex-col gap-2">
        <LinkButton name="dashboard" />
        <LinkButton name="table_page" />
        <LinkButton name="aparts" />
      </nav>
    </aside>
  );
}

