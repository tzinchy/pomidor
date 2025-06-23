import Aside from "../Navigation/Aside";

export default function HistoryPage(){
    return (
        <div className="bg-muted/60 flex min-h-screen w-full flex-col">
            <Aside />
            <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100">
                <CinTable />
            </main>
        </div>
    )
}