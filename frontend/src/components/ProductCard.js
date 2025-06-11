// src/components/ProductCard.js
import React from 'react';

const ProductCard = ({ id, title, price, imageUrl }) => {
  return (
    <div className="product-card">
      <img src={imageUrl} alt={title} />
      <h3>{title}</h3>
      <p>Price: ${price}</p>
    </div>
  );
};

export default ProductCard;