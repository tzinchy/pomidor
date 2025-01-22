import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import LeftBar from "./LeftBar";
import Aside from "../Navigation/Aside";
import ApartTable from "./ApartTable";

export default function ApartPage() {
  const [apartType, setApartType] = useState("FamilyStructure");
  const [collapsed, setCollapsed] = useState(false);
  const handleToggleSidebar = () => {
    setCollapsed(!collapsed);
  };

  const [districts, setDistricts] = useState([]);
  const [municipalDistricts, setMunicipalDistricts] = useState({});
  const [houseAddresses, setHouseAddresses] = useState({});
  const [apartments, setApartments] = useState([]);
  const [apartmentDetails, setApartmentDetails] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState({});
  const [searchTerm, setSearchTerm] = useState("");
  const detailsRef = useRef(null);
  const [selectedRow, setSelectedRow] = useState(-1);
  const [isDetailsVisible, setIsDetailsVisible] = useState(false);

  useEffect(() => {
    resetFilters();
    fetchDistricts();
  }, [apartType]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (detailsRef.current && !detailsRef.current.contains(e.target)) {
        setApartmentDetails(null);
      }
    };
    window.addEventListener("click", handleClickOutside);
    return () => window.removeEventListener("click", handleClickOutside);
  }, []);

  const resetFilters = () => {
    setExpandedNodes({});
    setMunicipalDistricts({});
    setHouseAddresses({});
    setApartments([]);
    setApartmentDetails(null);
    setSearchTerm("");
  };

  const fetchDistricts = async () => {
    try {
      const response = await axios.get(`/tables/district?apart_type=${apartType}`);
      setDistricts(response.data);
    } catch (error) {
      console.error("Error fetching districts:", error);
    }
  };

  const fetchMunicipalDistricts = async (district) => {
    try {
      const response = await axios.get(
        `/tables/municipal_district?apart_type=${apartType}&municipal_district=${district}`
      );
      setMunicipalDistricts((prev) => ({ ...prev, [district]: response.data }));
    } catch (error) {
      console.error("Error fetching municipal districts:", error);
    }
  };

  const fetchHouseAddresses = async (municipal) => {
    try {
      const response = await axios.get(
        `/tables/house_addresses?apart_type=${apartType}&areas=${municipal}`
      );
      setHouseAddresses((prev) => ({ ...prev, [municipal]: response.data }));
    } catch (error) {
      console.error("Error fetching house addresses:", error);
    }
  };

  const fetchApartments = async (addresses) => {
    try {
      const response = await axios.get(
        `/tables/apartments?apart_type=${apartType}&house_addresses=${addresses.join(",")}`
      );
      setApartments(response.data);
    } catch (error) {
      console.error("Error fetching apartments:", error);
    }
  };

  const fetchApartmentDetails = async (apartmentId) => {
    console.log(apartmentId);
    try {
      const response = await axios.get(
        `/tables/apartment/${apartmentId}?apart_type=${apartType}`
      );
      setApartmentDetails(response.data);
      console.log(response.data);
    } catch (error) {
      console.error("Error fetching apartment details:", error);
    }
  };

  const filteredApartments = apartments.filter((apt) =>
    String(apt.new_apart_id).toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-muted/60 flex min-h-screen w-full flex-col">
      <Aside />
      <main className="relative flex flex-1 flex-col gap-4 p-2 sm:pl-16 bg-neutral-100">
        <div className="flex flex-col lg:flex-row bg-white text-gray-800 relative min-h-[98vh]">
          {/* Сайдбар */}
          
            <LeftBar
              apartType={apartType}
              setApartType={setApartType}
              collapsed={collapsed}
              handleToggleSidebar={handleToggleSidebar}
              districts={districts}
              municipalDistricts={municipalDistricts}
              fetchMunicipalDistricts={fetchMunicipalDistricts}
              houseAddresses={houseAddresses}
              fetchHouseAddresses={fetchHouseAddresses}
              expandedNodes={expandedNodes}
              setExpandedNodes={setExpandedNodes}
              fetchApartments={fetchApartments}
              setSelectedRow={setSelectedRow}
              setIsDetailsVisible={setIsDetailsVisible}
            />
          

          {/* Таблица */}
          <div className="flex-1 overflow-auto">
            <ApartTable
              apartType={apartType}
              data={filteredApartments}
              fetchApartmentDetails={fetchApartmentDetails}
              apartmentDetails={apartmentDetails}
              detailsRef={detailsRef}
              selectedRow={selectedRow}
              setSelectedRow={setSelectedRow}
              isDetailsVisible={isDetailsVisible} 
              setIsDetailsVisible={setIsDetailsVisible}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
