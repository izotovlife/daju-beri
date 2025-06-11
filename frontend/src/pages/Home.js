// src/pages/Home.js
import React, { useEffect, useState } from 'react';
import { fetchProducts } from '../services/api';
import ProductsList from '../components/ProductsList';

const Home = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const result = await fetchProducts();
      setProducts(result);
    };
    fetchData();
  }, []);

  return (
    <div className="home-page">
      <h1>Our Special Offers</h1>
      <ProductsList products={products} />
    </div>
  );
};

export default Home;