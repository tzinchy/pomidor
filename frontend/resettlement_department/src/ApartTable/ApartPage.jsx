import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import LeftBar from "./LeftBar";
import Aside from "../Navigation/Aside";
import ApartTable from "./ApartTable";
import { HOSTLINK } from "..";

const APART_TYPES = {
  NEW: "NewApartment",
  OLD: "FamilyStructure"
};

const paramsSerializer = {
  indexes: null,
  encode: (value) => encodeURIComponent(value)
};

export default function ApartPage() {
  const [apartType, setApartType] = useState(APART_TYPES.OLD);
  const [collapsed, setCollapsed] = useState(false);
  const [districts, setDistricts] = useState([]);
  const [municipalDistricts, setMunicipalDistricts] = useState({});
  const [houseAddresses, setHouseAddresses] = useState({});
  const [apartments, setApartments] = useState([]);
  const [apartmentDetails, setApartmentDetails] = useState(null);
  const [expandedNodes, setExpandedNodes] = useState({});
  const [searchTerm, setSearchTerm] = useState("");
  const detailsRef = useRef(null);
  const [selectedRow, setSelectedRow] = useState(false);
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
      const response = await axios.get(`${HOSTLINK}/tables/district`, {
        params: { apart_type: apartType },
        paramsSerializer
      });
      setDistricts(response.data);
    } catch (error) {
      console.error("Error fetching districts:", error.response?.data);
    }
  };

  const fetchMunicipalDistricts = async (district) => {
    try {
      const response = await axios.get(`${HOSTLINK}/tables/municipal_district`, {
        params: {
          apart_type: apartType,
          district: [district] // Исправленное имя параметра
        },
        paramsSerializer
      });
      setMunicipalDistricts(prev => ({
        ...prev,
        [district]: response.data
      }));
    } catch (error) {
      console.error("Error fetching municipal districts:", error.response?.data);
    }
  };

  const fetchHouseAddresses = async (municipal) => {
    try {
      const response = await axios.get(`${HOSTLINK}/tables/house_addresses`, {
        params: {
          apart_type: apartType,
          municipal_district: [municipal]
        },
        paramsSerializer
      });
      setHouseAddresses(prev => ({
        ...prev,
        [municipal]: response.data
      }));
    } catch (error) {
      console.error("Error fetching house addresses:", error.response?.data);
    }
  };

  const fetchApartments = async (addresses, municipal_districts) => {
    try {
      const response = await axios.get(`${HOSTLINK}/tables/apartments`, {
        params: {
          apart_type: apartType,
          house_addresses: addresses,
          districts: [],
          municipal_districts: municipal_districts
        },
        paramsSerializer
      });
      setApartments(response.data);
    } catch (error) {
      console.error("Error fetching apartments:", error.response?.data);
    }
  };

  const fetchApartmentDetails = async (apartmentId) => {
    try {
      const response = await axios.get(
        `${HOSTLINK}/tables/apartment/${apartmentId}`,
        { 
          params: { apart_type: apartType },
          paramsSerializer
        }
      );
      setApartmentDetails(response.data);
    } catch (error) {
      console.error("Error fetching apartment details:", error.response?.data);
    }
  };

  const filteredApartments = apartments.filter(apt =>
    String(apt.new_apart_id).toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleToggleSidebar = () => setCollapsed(!collapsed);

  return (
    <div className="bg-muted/60 flex min-h-screen w-full flex-col">
      <Aside />
      <main className="relative flex flex-1 flex-col gap-4 p-2 sm:pl-16 bg-neutral-100">
        <div className="flex flex-col lg:flex-row bg-white text-gray-800 relative min-h-[98vh]">
          <LeftBar
            apartType={apartType}
            setApartType={setApartType}
            APART_TYPES={APART_TYPES}
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