import React, { useState, useEffect } from "react";
import Aside from "../Navigation/Aside";
import Card from "./Card";
import BarChart from "./RiskChart";

export default function Dashboard_page() {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Отправка запроса на FastAPI
        fetch("/dashboard/dashboard") // полный путь к маршруту
          .then((response) => {
            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
          })
          .then((fetchedData) => {
            setData(fetchedData);
            setIsLoading(false);
          })
          .catch((err) => {
            console.error("Error fetching data:", err);
            setIsLoading(false);
          });
      }, []);

    return (
      <div className="bg-muted/60 flex min-h-screen w-full flex-col">
        <Aside />
        <main className="relative flex flex-1 flex-col gap-2 p-2 sm:pl-16 bg-neutral-100">
            <div className="flex space-x-16 justify-center m-8">
                {isLoading ? (
                    <p>Loading data...</p>
                ) : (
                    data[0].map((value) => <Card value={value} />)
                )}
            </div>
            
            {isLoading ? (
                    <p></p>
                ) : (
                    <BarChart chartData={data[1]} />
                )}
        </main>
      </div>
    );
}
