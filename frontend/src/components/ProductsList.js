// src/components/ProductsList.js
import React from 'react';
import ProductCard from './ProductCard';

const ProductsList = ({ products }) => {
  return (
    <div className="products-list">
      {products.map(product => (
        <ProductCard key={product.id} {...product} />
      ))}
    </div>
  );
};

export default ProductsList;