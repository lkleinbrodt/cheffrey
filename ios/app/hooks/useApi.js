import { useState } from "react";

export default useApi = (apiFunc) => {
  const [data, setData] = useState([]);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  const request = async (...args) => {
    setLoading(true);
    const response = await apiFunc(...args);
    if (!response.ok) return setError(true);
    setData(response.data);
    setLoading(false);
  };

  return { data, loading, error, request };
};
// const getListingAPI = useAPI(listingAPI.getListings);
//getListingAPI.request(1,2,3);
//getListingAPI.data;
//getListingAPI.loading; etc.
